# -*- coding: utf-8 -*-
"""
Lookup dialog for ENVI Auto Fill Fields
"""

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QTextBrowser, QThread, pyqtSignal, QSpacerItem, QSizePolicy, QCheckBox
)
from aqt.utils import showInfo
import json
from typing import Any, Dict
from . import api


def esc(s: Any) -> str:
    """Escape HTML characters"""
    s = "" if s is None else str(s)
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#039;")
    )


def render_html(word: str, payload: Dict[str, Any], show_raw: bool) -> str:
    """Render API response as HTML"""
    definition = esc((payload.get("def") or "").strip())
    mean = payload.get("mean")
    
    pos_val = esc((payload.get("pos") or "").strip())
    pron_val = esc((payload.get("pron") or "").strip())
    
    blocks = []
    
    # Summary pills
    pills = []
    if pos_val:
        pills.append(
            "<span style='display:inline-block; padding:2px 8px; border:1px solid #ddd; "
            "border-radius:999px; margin-right:8px;'><b>POS:</b> " + pos_val + "</span>"
        )
    if pron_val:
        pv = pron_val
        if "/" not in pv and any(c in pv for c in ["ˈ", "ː", "ɜ", "ə"]):
            pv = f"/{pv}/"
        pills.append(
            "<span style='display:inline-block; padding:2px 8px; border:1px solid #ddd; "
            "border-radius:999px;'><b>IPA:</b> " + pv + "</span>"
        )
    
    if pills:
        blocks.append("<div style='margin:6px 0 14px 0;'>" + "".join(pills) + "</div>")
    
    if definition:
        blocks.append(f"<div><b>Definition:</b><br/>{definition}</div>")
    
    if isinstance(mean, list) and mean:
        items_html = []
        for i, it in enumerate(mean[:10], start=1):
            if not isinstance(it, dict):
                continue
            
            m = esc((it.get("m") or "").strip())
            e = esc((it.get("e") or "").strip())
            v = esc((it.get("v") or "").strip())
            
            row = [f"<div style='margin:10px 0; padding:10px; border:1px solid #ddd; border-radius:12px;'>"]
            row.append(f"<div style='margin-bottom:6px;'><b>{i}.</b></div>")
            if m:
                row.append(f"<div style='margin-top:6px;'><b>Meaning:</b> {m}</div>")
            if v:
                row.append(f"<div style='margin-top:6px;'><b>Vietnamese:</b> {v}</div>")
            if e:
                row.append(f"<div style='margin-top:6px;'><b>Example:</b><br/>{e}</div>")
            row.append("</div>")
            items_html.append("".join(row))
        
        blocks.append("<div style='margin-top:12px;'><b>Results:</b></div>" + "".join(items_html))
    
    if show_raw:
        raw = esc(json.dumps(payload, ensure_ascii=False, indent=2))
        blocks.append("<details style='margin-top:14px;'><summary><b>Raw JSON</b></summary>"
                      "<pre style='white-space:pre-wrap; font-size:12px;'>" + raw + "</pre></details>")
    
    return (
        "<div style='font-family:Segoe UI, Arial; font-size:13px;'>"
        f"<div style='font-size:16px; margin-bottom:8px;'><b>{esc(word)}</b></div>"
        + "".join(blocks)
        + "</div>"
    )


class LookupWorker(QThread):
    """Worker thread for API lookup"""
    ok = pyqtSignal(str)
    err = pyqtSignal(str)
    
    def __init__(self, word: str, show_raw: bool):
        super().__init__()
        self.word = word
        self.show_raw = show_raw
    
    def run(self) -> None:
        try:
            payload = api.search_english(self.word)
            html = render_html(self.word, payload, self.show_raw)
            self.ok.emit(html)
        except Exception as e:
            self.err.emit(str(e))


class LookupDialog(QDialog):
    """Simple lookup dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("ENVI Auto Fill - Lookup")
        self.setMinimumSize(760, 660)
        
        self._setup_ui()
        self.worker = None
    
    def _setup_ui(self):
        """Setup UI components"""
        root = QVBoxLayout(self)
        
        # Top section: input
        top = QHBoxLayout()
        top.addWidget(QLabel("Word:"))
        self.inp = QLineEdit()
        self.inp.setPlaceholderText("Type an English word (e.g., 'intense')")
        top.addWidget(self.inp, 1)
        self.btn = QPushButton("Lookup")
        top.addWidget(self.btn)
        root.addLayout(top)
        
        # Options
        opts = QHBoxLayout()
        self.chk_raw = QCheckBox("Show raw JSON")
        opts.addWidget(self.chk_raw)
        opts.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        root.addLayout(opts)
        
        # Status
        self.status = QLabel("")
        root.addWidget(self.status)
        
        # Output
        self.out = QTextBrowser()
        self.out.setOpenExternalLinks(True)
        root.addWidget(self.out, 1)
        
        # Bottom buttons
        bottom = QHBoxLayout()
        bottom.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.btn_close = QPushButton("Close")
        bottom.addWidget(self.btn_close)
        root.addLayout(bottom)
        
        # Connect signals
        self.btn.clicked.connect(self.lookup)
        self.inp.returnPressed.connect(self.lookup)
        self.btn_close.clicked.connect(self.close)
    
    def lookup(self):
        """Perform lookup"""
        word = (self.inp.text() or "").strip()
        if not word:
            showInfo("Please type a word to look up.")
            return
        
        self.status.setText("Looking up…")
        self.btn.setEnabled(False)
        self.out.setHtml("")
        
        self.worker = LookupWorker(word, self.chk_raw.isChecked())
        self.worker.ok.connect(self._on_ok)
        self.worker.err.connect(self._on_err)
        self.worker.start()
    
    def _on_ok(self, html: str):
        """Handle successful lookup"""
        self.out.setHtml(html)
        self.status.setText("Done.")
        self.btn.setEnabled(True)
    
    def _on_err(self, msg: str):
        """Handle lookup error"""
        self.out.setHtml(f"<div style='color:#b00020'><b>Error:</b> {esc(msg)}</div>")
        self.status.setText("Failed.")
        self.btn.setEnabled(True)
