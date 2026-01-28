# -*- coding: utf-8 -*-
"""
ENVI Auto Fill Fields - Anki Addon
Version: 1.0.0
Author: Nguyễn Văn Phán

Automatically fills vocabulary fields in Anki cards using ENVI dictionary API
"""

from aqt import mw, gui_hooks
from aqt.qt import QAction, QMenu
from aqt.utils import showInfo
from aqt.browser import Browser
from aqt.reviewer import Reviewer
from anki.hooks import wrap
from typing import List

from . import config
from .lookup_dialog import LookupDialog
from .settings_dialog import SettingsDialog
from .about_dialog import AboutDialog
from .processor import CardProcessor, process_single_note


# Global instances
_lookup_dialog = None
_settings_dialog = None
_about_dialog = None
_processor = CardProcessor()


def show_lookup_dialog():
    """Show lookup dialog"""
    global _lookup_dialog
    if _lookup_dialog is None:
        _lookup_dialog = LookupDialog()
    _lookup_dialog.show()
    _lookup_dialog.raise_()
    _lookup_dialog.activateWindow()


def show_settings_dialog():
    """Show settings dialog"""
    global _settings_dialog
    _settings_dialog = SettingsDialog()
    _settings_dialog.exec()


def show_about_dialog():
    """Show about dialog"""
    global _about_dialog
    _about_dialog = AboutDialog()
    _about_dialog.exec()


def setup_menu():
    """Setup addon menu in Tools"""
    # Create submenu
    menu = QMenu("ENVI Auto Fill", mw)
    
    # Lookup action
    lookup_action = QAction("Lookup", mw)
    lookup_action.triggered.connect(show_lookup_dialog)
    menu.addAction(lookup_action)
    
    # Settings action
    settings_action = QAction("Settings", mw)
    settings_action.triggered.connect(show_settings_dialog)
    menu.addAction(settings_action)
    
    # About action
    about_action = QAction("About", mw)
    about_action.triggered.connect(show_about_dialog)
    menu.addAction(about_action)
    
    # Add to Tools menu
    mw.form.menuTools.addMenu(menu)


def on_reviewer_show_question(card):
    """Hook for when question is shown in reviewer"""
    if not config.is_enabled() or not config.is_configured():
        return
    
    # Process the note in background
    try:
        process_single_note(card.note().id)
    except Exception as e:
        print(f"Error in reviewer hook: {e}")


def setup_browser_menu(browser: Browser):
    """Setup context menu in browser"""
    menu = browser.form.menuEdit
    
    # Add separator
    menu.addSeparator()
    
    # Add action
    action = QAction("ENVI Auto Fill - Process Cards", browser)
    action.triggered.connect(lambda: on_browser_process(browser))
    menu.addAction(action)


def on_browser_process(browser: Browser):
    """Handle processing from browser"""
    if not config.is_configured():
        showInfo(
            "Please configure the addon first via Tools → ENVI Auto Fill → Settings",
            parent=browser
        )
        return
    
    # Get selected notes
    note_ids = browser.selected_notes()
    
    if not note_ids:
        showInfo("Please select at least one card.", parent=browser)
        return
    
    # Process
    _processor.process_notes(note_ids, parent=browser)


def init_addon():
    """Initialize addon"""
    # Setup menu
    setup_menu()
    
    # Setup reviewer hook
    gui_hooks.reviewer_did_show_question.append(on_reviewer_show_question)
    
    # Setup browser hook
    gui_hooks.browser_menus_did_init.append(setup_browser_menu)
    
    print("ENVI Auto Fill Fields addon loaded successfully")


# Initialize when profile is loaded
try:
    gui_hooks.profile_did_open.append(init_addon)
except Exception:
    init_addon()
