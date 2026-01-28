# -*- coding: utf-8 -*-
"""
About dialog for ENVI Auto Fill Fields
"""

from aqt import mw
from aqt.qt import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout


class AboutDialog(QDialog):
    """About dialog showing addon information"""
    
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("About - ENVI Auto Fill")
        self.setMinimumWidth(400)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<h2>ENVI Auto Fill Fields</h2>")
        title.setStyleSheet("color: #1976D2;")
        layout.addWidget(title)
        
        # Version
        version = QLabel("<b>Version:</b> 1.0.1")
        layout.addWidget(version)
        
        layout.addSpacing(10)
        
        # Author
        author = QLabel("<b>Author:</b> Nguyễn Văn Phán")
        layout.addWidget(author)
        
        layout.addSpacing(10)
        
        # Description
        desc = QLabel(
            "Addon tự động điền thông tin từ vựng vào các trường dữ liệu của thẻ Anki.\n\n"
            "Tính năng:\n"
            "• Tra cứu từ vựng tiếng Anh\n"
            "• Tự động điền nghĩa, phát âm, loại từ, ví dụ\n"
            "• Hỗ trợ cả chế độ review và browser\n"
            "• Cấu hình linh hoạt cho từng note type"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(10)
        
        # API info
        api_info = QLabel(
            "<i>Sử dụng API từ: en.jpdictionary.com</i>"
        )
        layout.addWidget(api_info)
        
        layout.addStretch()
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
