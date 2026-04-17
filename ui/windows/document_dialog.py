import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel
from PySide6.QtCore import Qt
import core.constants as const

class DocumentDialog(QDialog):
    """A reusable accessible dialog for displaying Markdown/Text documents like Help or Changelog."""
    
    def __init__(self, title: str, filename: str, view_model, parent=None):
        super().__init__(parent)
        self.title = title
        self.filename = filename
        self.view_model = view_model
        
        self._setup_ui()
        self._load_content()

    def _setup_ui(self):
        self.setWindowTitle(self.title)
        self.setMinimumSize(600, 500)
        self.setModal(True) # يمنع التفاعل مع اللعبة حتى يتم إغلاق هذه النافذة

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title Label
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("screen_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        layout.addWidget(self.title_label)

        # Text Area (Read Only)
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.text_area.setAccessibleName(f"محتوى {self.title}")
        self.text_area.setStyleSheet("font-size: 16px; padding: 10px;")
        layout.addWidget(self.text_area)

        # Close Button
        btn_layout = QHBoxLayout()
        self.close_btn = QPushButton("إغلاق")
        self.close_btn.setObjectName("action_button")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _load_content(self):
        """Loads the text from the specified file in the assets/docs directory."""
        file_path = os.path.join(const.BASE_DIR, "assets", "docs", self.filename)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.text_area.setMarkdown(content) # يدعم تنسيق الماركدوان تلقائياً
            except Exception as e:
                self.text_area.setPlainText(f"حدث خطأ أثناء قراءة الملف:\n{str(e)}")
        else:
            self.text_area.setPlainText(f"عذراً، لم يتم العثور على ملف: {self.filename}")
            
        # نطق العنوان لتنبيه المكفوفين بفتح النافذة
        self.view_model.read_text(f"تم فتح شاشة {self.title}، استخدم مفتاح التبويب للتنقل.", interrupt=True)
