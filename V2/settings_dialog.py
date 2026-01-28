# -*- coding: utf-8 -*-
"""
Settings dialog for ENVI Auto Fill Fields
"""

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QCheckBox, QGroupBox, QFormLayout, QMessageBox
)
from typing import Optional, List, Dict
from . import config


class SettingsDialog(QDialog):
    """Settings dialog for configuring the addon"""
    
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("ENVI Auto Fill - Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.current_config = config.get_config()
        self.note_types = self._get_note_types()
        
        self._setup_ui()
        self._load_settings()
    
    def _get_note_types(self) -> List[str]:
        """Get list of available note types"""
        return sorted([nt['name'] for nt in mw.col.models.all()])
    
    def _get_note_fields(self, note_type_name: str) -> List[str]:
        """Get fields for a specific note type"""
        if not note_type_name:
            return []
        
        model = mw.col.models.by_name(note_type_name)
        if not model:
            return []
        
        return [field['name'] for field in model['flds']]
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        
        # Enable/Disable addon
        self.chk_enabled = QCheckBox("Enable Auto Fill")
        self.chk_enabled.setToolTip("Enable or disable the addon")
        layout.addWidget(self.chk_enabled)
        
        # Overwrite option
        self.chk_overwrite = QCheckBox("Overwrite existing data")
        self.chk_overwrite.setToolTip("If checked, existing field data will be overwritten")
        layout.addWidget(self.chk_overwrite)
        
        # Show POS in meanings option
        self.chk_show_pos = QCheckBox("Show POS tags in meanings (e.g., [noun] nghĩa)")
        self.chk_show_pos.setToolTip("If checked, meanings will include part of speech tags")
        layout.addWidget(self.chk_show_pos)
        
        layout.addSpacing(10)
        
        # Note type selection
        note_type_group = QGroupBox("Note Type Configuration")
        note_type_layout = QFormLayout()
        
        self.combo_note_type = QComboBox()
        self.combo_note_type.addItem("-- Select Note Type --", "")
        for nt in self.note_types:
            self.combo_note_type.addItem(nt, nt)
        self.combo_note_type.currentIndexChanged.connect(self._on_note_type_changed)
        note_type_layout.addRow("Note Type:", self.combo_note_type)
        
        note_type_group.setLayout(note_type_layout)
        layout.addWidget(note_type_group)
        
        # Field mapping
        field_group = QGroupBox("Field Mapping")
        field_layout = QFormLayout()
        
        self.combo_word = QComboBox()
        field_layout.addRow("Word Field (source):", self.combo_word)
        
        self.combo_definition = QComboBox()
        field_layout.addRow("Definition Field:", self.combo_definition)
        
        self.combo_pronunciation = QComboBox()
        field_layout.addRow("Pronunciation Field:", self.combo_pronunciation)
        
        self.combo_pos = QComboBox()
        field_layout.addRow("Part of Speech Field:", self.combo_pos)
        
        self.combo_meanings = QComboBox()
        field_layout.addRow("Meanings Field:", self.combo_meanings)
        
        self.combo_examples = QComboBox()
        field_layout.addRow("Examples Field:", self.combo_examples)
        
        field_group.setLayout(field_layout)
        layout.addWidget(field_group)
        
        # Info label
        info_label = QLabel(
            "<i>Note: The 'Word Field' is where the addon will look for words to search. "
            "Other fields will be filled with the lookup results.</i>"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self._on_save)
        button_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(button_layout)
    
    def _on_note_type_changed(self, index: int):
        """Handle note type selection change"""
        note_type_name = self.combo_note_type.currentData()
        fields = self._get_note_fields(note_type_name)
        
        # Update all field combo boxes
        combos = [
            self.combo_word,
            self.combo_definition,
            self.combo_pronunciation,
            self.combo_pos,
            self.combo_meanings,
            self.combo_examples
        ]
        
        for combo in combos:
            combo.clear()
            combo.addItem("-- Not mapped --", "")
            for field in fields:
                combo.addItem(field, field)
    
    def _load_settings(self):
        """Load current settings into UI"""
        # Enable/Disable
        self.chk_enabled.setChecked(self.current_config.get("enabled", True))
        
        # Overwrite
        self.chk_overwrite.setChecked(self.current_config.get("overwrite", True))
        
        # Show POS in meanings
        self.chk_show_pos.setChecked(self.current_config.get("show_pos_in_meanings", True))
        
        # Note type
        note_type = self.current_config.get("note_type", "")
        if note_type:
            index = self.combo_note_type.findData(note_type)
            if index >= 0:
                self.combo_note_type.setCurrentIndex(index)
        
        # Field mapping
        field_mapping = self.current_config.get("field_mapping", {})
        
        self._set_combo_value(self.combo_word, field_mapping.get("word", ""))
        self._set_combo_value(self.combo_definition, field_mapping.get("definition", ""))
        self._set_combo_value(self.combo_pronunciation, field_mapping.get("pronunciation", ""))
        self._set_combo_value(self.combo_pos, field_mapping.get("pos", ""))
        self._set_combo_value(self.combo_meanings, field_mapping.get("meanings", ""))
        self._set_combo_value(self.combo_examples, field_mapping.get("examples", ""))
    
    def _set_combo_value(self, combo: QComboBox, value: str):
        """Set combo box to specific value"""
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)
    
    def _on_save(self):
        """Save settings"""
        note_type = self.combo_note_type.currentData()
        word_field = self.combo_word.currentData()
        
        # Validation
        if not note_type:
            QMessageBox.warning(
                self,
                "Invalid Configuration",
                "Please select a Note Type."
            )
            return
        
        if not word_field:
            QMessageBox.warning(
                self,
                "Invalid Configuration",
                "Please select a Word Field (source field for lookup)."
            )
            return
        
        # Build config
        new_config = {
            "enabled": self.chk_enabled.isChecked(),
            "overwrite": self.chk_overwrite.isChecked(),
            "show_pos_in_meanings": self.chk_show_pos.isChecked(),
            "note_type": note_type,
            "field_mapping": {
                "word": word_field,
                "definition": self.combo_definition.currentData(),
                "pronunciation": self.combo_pronunciation.currentData(),
                "pos": self.combo_pos.currentData(),
                "meanings": self.combo_meanings.currentData(),
                "examples": self.combo_examples.currentData()
            }
        }
        
        # Save
        config.save_config(new_config)
        
        QMessageBox.information(
            self,
            "Settings Saved",
            "Settings have been saved successfully."
        )
        
        self.accept()
