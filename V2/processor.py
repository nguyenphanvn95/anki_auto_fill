# -*- coding: utf-8 -*-
"""
Card processor for auto-filling fields
"""

from aqt import mw
from aqt.qt import QThread, pyqtSignal, QProgressDialog
from anki.notes import Note
from typing import List, Dict, Optional
from . import api, config
import traceback


class ProcessWorker(QThread):
    """Worker thread for processing cards"""
    
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(int, int)  # success_count, error_count
    error = pyqtSignal(str, str)  # card_info, error_message
    
    def __init__(self, note_ids: List[int]):
        super().__init__()
        self.note_ids = note_ids
        self.should_stop = False
    
    def run(self):
        """Process all notes"""
        total = len(self.note_ids)
        success_count = 0
        error_count = 0
        
        note_type_name = config.get_note_type_name()
        field_mapping = config.get_field_mapping()
        should_overwrite = config.should_overwrite()
        show_pos_tags = config.show_pos_in_meanings()
        
        word_field = field_mapping.get("word", "")
        
        if not word_field:
            self.error.emit("Configuration", "Word field not configured")
            self.finished.emit(0, total)
            return
        
        for i, note_id in enumerate(self.note_ids):
            if self.should_stop:
                break
            
            try:
                note = mw.col.get_note(note_id)
                
                # Check if note type matches
                if note.note_type()['name'] != note_type_name:
                    continue
                
                # Check if word field exists
                if word_field not in note:
                    continue
                
                word = note[word_field].strip()
                if not word:
                    continue
                
                self.progress.emit(i + 1, total, f"Processing: {word}")
                
                # Check if we should skip (all fields already filled and not overwriting)
                if not should_overwrite:
                    all_filled = True
                    for field_key, field_name in field_mapping.items():
                        if field_key == "word" or not field_name:
                            continue
                        if field_name in note and not note[field_name].strip():
                            all_filled = False
                            break
                    
                    if all_filled:
                        success_count += 1
                        continue
                
                # Lookup word
                try:
                    payload = api.search_english(word)
                    data = api.extract_data(payload, show_pos_tags)
                    
                    # Fill fields
                    updated = False
                    for field_key, field_name in field_mapping.items():
                        if field_key == "word" or not field_name:
                            continue
                        
                        if field_name not in note:
                            continue
                        
                        # --- Robust key lookup (fallback aliases) ---
                        def _get_value(data_dict, key):
                            if not data_dict:
                                return ""

                            # direct hit first
                            v = data_dict.get(key, "")
                            if v:
                                return v

                            # aliases by logical field key
                            aliases = {
                                "pronunciation": ["ipa", "IPA", "pron"],
                                "ipa": ["pronunciation", "IPA", "pron"],
                                "IPA": ["pronunciation", "ipa", "pron"],
                                "pron": ["pronunciation", "ipa", "IPA"],

                                "part_of_speech": ["pos", "partOfSpeech"],
                                "pos": ["part_of_speech", "partOfSpeech"],
                                "partOfSpeech": ["part_of_speech", "pos"],

                                "definition": ["def", "sources", "Sources"],
                                "def": ["definition", "sources", "Sources"],
                                "sources": ["definition", "def", "Sources"],
                                "Sources": ["definition", "def", "sources"],

                                "meanings": ["meaning", "Meaning"],
                                "examples": ["example", "Example"],
                            }

                            for k in aliases.get(key, []):
                                v2 = data_dict.get(k, "")
                                if v2:
                                    return v2
                            return ""

                        value = _get_value(data, field_key)

                        if not value:
                            continue
                        
                        # Check if should update
                        if should_overwrite or not note[field_name].strip():
                            note[field_name] = value
                            updated = True
                    
                    if updated:
                        mw.col.update_note(note)
                    
                    success_count += 1
                    
                except Exception as e:
                    error_msg = f"Lookup failed: {str(e)}"
                    self.error.emit(word, error_msg)
                    error_count += 1
            
            except Exception as e:
                error_msg = f"Processing error: {str(e)}\n{traceback.format_exc()}"
                self.error.emit(f"Note ID: {note_id}", error_msg)
                error_count += 1
        
        self.finished.emit(success_count, error_count)
    
    def stop(self):
        """Stop processing"""
        self.should_stop = True


class CardProcessor:
    """Process cards to auto-fill fields"""
    
    def __init__(self):
        self.worker = None
        self.progress_dialog = None
        self.errors = []
    
    def process_notes(self, note_ids: List[int], parent=None):
        """Process multiple notes"""
        if not config.is_configured():
            from aqt.utils import showInfo
            showInfo(
                "Please configure the addon first via Tools → ENVI Auto Fill → Settings",
                parent=parent
            )
            return
        
        if not config.is_enabled():
            from aqt.utils import showInfo
            showInfo("Addon is currently disabled. Enable it in Settings.", parent=parent)
            return
        
        self.errors = []
        
        # Create progress dialog
        self.progress_dialog = QProgressDialog(
            "Processing cards...",
            "Cancel",
            0,
            len(note_ids),
            parent or mw
        )
        self.progress_dialog.setWindowTitle("ENVI Auto Fill")
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        
        # Create and start worker
        self.worker = ProcessWorker(note_ids)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.progress_dialog.canceled.connect(self.worker.stop)
        
        self.worker.start()
    
    def _on_progress(self, current: int, total: int, message: str):
        """Update progress"""
        if self.progress_dialog:
            self.progress_dialog.setMaximum(total)
            self.progress_dialog.setValue(current)
            self.progress_dialog.setLabelText(message)
    
    def _on_error(self, card_info: str, error_msg: str):
        """Handle error"""
        self.errors.append(f"{card_info}: {error_msg}")
    
    def _on_finished(self, success_count: int, error_count: int):
        """Handle completion"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        from aqt.utils import showInfo
        
        message = f"Processing completed!\n\n"
        message += f"Success: {success_count}\n"
        message += f"Errors: {error_count}\n"
        
        if self.errors:
            message += f"\nError details:\n"
            message += "\n".join(self.errors[:10])  # Show first 10 errors
            if len(self.errors) > 10:
                message += f"\n... and {len(self.errors) - 10} more errors"
        
        showInfo(message, parent=mw)


def process_single_note(note_id: int) -> bool:
    """
    Process a single note
    Returns True if successful, False otherwise
    """
    if not config.is_enabled():
        return False
    
    note_type_name = config.get_note_type_name()
    field_mapping = config.get_field_mapping()
    should_overwrite = config.should_overwrite()
    show_pos_tags = config.show_pos_in_meanings()
    
    word_field = field_mapping.get("word", "")
    if not word_field:
        return False
    
    try:
        note = mw.col.get_note(note_id)
        
        # Check if note type matches
        if note.note_type()['name'] != note_type_name:
            return False
        
        # Check if word field exists
        if word_field not in note:
            return False
        
        word = note[word_field].strip()
        if not word:
            return False
        
        # Check if we should skip
        if not should_overwrite:
            all_filled = True
            for field_key, field_name in field_mapping.items():
                if field_key == "word" or not field_name:
                    continue
                if field_name in note and not note[field_name].strip():
                    all_filled = False
                    break
            
            if all_filled:
                return True
        
        # Lookup and fill
        payload = api.search_english(word)
        data = api.extract_data(payload, show_pos_tags)
        
        updated = False
        for field_key, field_name in field_mapping.items():
            if field_key == "word" or not field_name:
                continue
            
            if field_name not in note:
                continue
            
            value = data.get(field_key, "")
            if not value:
                continue
            
            if should_overwrite or not note[field_name].strip():
                note[field_name] = value
                updated = True
        
        if updated:
            mw.col.update_note(note)
        
        return True
    
    except Exception as e:
        print(f"Error processing note {note_id}: {e}")
        traceback.print_exc()
        return False
