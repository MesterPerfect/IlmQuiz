import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap

class AboutScreen(QWidget):
    """Displays information about the application and the developer."""
    
    back_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for smaller screens
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(25)

        # Header with Back Button
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("عودة")
        self.back_btn.setObjectName("back_button")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        
        self.title_label = QLabel("حول البرنامج")
        self.title_label.setObjectName("screen_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title_label, 1)
        self.content_layout.addLayout(header_layout)

        # App Info Section
        self.app_name_label = QLabel("IlmQuiz v1.0.0")
        self.app_name_label.setObjectName("about_app_name")
        self.app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_name_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout.addWidget(self.app_name_label)

        self.desc_label = QLabel(
            "لعبة مسابقات ثقافية إسلامية تفاعلية، تهدف إلى إثراء معرفتك الدينية بطريقة ممتعة وشيقة. "
            "تم تصميم اللعبة لتكون متوافقة تماماً مع قارئات الشاشة لتوفير تجربة شاملة للجميع."
        )
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout.addWidget(self.desc_label)

        # Developer Section Separator
        self.content_layout.addWidget(self._create_separator())
        
        self.dev_title_label = QLabel("عن المطور")
        self.dev_title_label.setObjectName("about_section_title")
        self.dev_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dev_title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout.addWidget(self.dev_title_label)

        # Profile Picture Setup
        self.profile_pic = QLabel()
        self.profile_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Determine the image path from the assets folder
        image_path = os.path.join("assets", "images", "profile.jpg")
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(
                120, 120, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.profile_pic.setPixmap(pixmap)
        else:
            # Fallback if the image is missing
            self.profile_pic.setText("[صورة المطور]")
            self.profile_pic.setFixedSize(120, 120)
            self.profile_pic.setStyleSheet("background-color: #333; color: #fff; border-radius: 60px;")
            
        self.content_layout.addWidget(self.profile_pic, alignment=Qt.AlignmentFlag.AlignCenter)

        self.dev_name_label = QLabel("MesterPerfect")
        self.dev_name_label.setObjectName("about_dev_name")
        self.dev_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dev_name_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout.addWidget(self.dev_name_label)

        # Social Buttons Layout
        social_layout = QHBoxLayout()
        social_layout.setSpacing(15)
        social_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create buttons with URLs
        self.btn_github = self._create_social_button("GitHub", "https://github.com/MesterPerfect")
        self.btn_telegram = self._create_social_button("Telegram", "https://t.me/MesterPerfect")
        self.btn_x = self._create_social_button("X (Twitter)", "https://x.com/MesterPerfect")
        self.btn_facebook = self._create_social_button("Facebook", "https://facebook.com/MesterPerfect")
        
        social_layout.addWidget(self.btn_github)
        social_layout.addWidget(self.btn_telegram)
        social_layout.addWidget(self.btn_x)
        social_layout.addWidget(self.btn_facebook)
        
        self.content_layout.addLayout(social_layout)

        # Support Section Separator
        self.content_layout.addWidget(self._create_separator())
        
        self.support_title = QLabel("دعم المشروع")
        self.support_title.setObjectName("about_section_title")
        self.support_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.support_title.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout.addWidget(self.support_title)

        self.support_desc = QLabel(
            "يسعدني جداً دعمكم لاستمرار هذا المشروع مفتوح المصدر. يمكنك دعمي من خلال:\n\n"
            "1. إضافة نجمة (Star) للمشروع على منصة GitHub.\n"
            "2. الإبلاغ عن الأخطاء (Issues) عبر المستودع.\n"
            "3. مشاركة اللعبة مع أصدقائك لتعم الفائدة."
        )
        self.support_desc.setWordWrap(True)
        self.support_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.support_desc.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout.addWidget(self.support_desc)

        # Copyright Footer
        self.content_layout.addStretch()
        self.footer_label = QLabel("حقوق النشر © 2026؛ MesterPerfect. جميع الحقوق محفوظة.")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout.addWidget(self.footer_label)

        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)

    def _create_separator(self) -> QFrame:
        """Creates a styled horizontal line to separate sections."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #444; max-height: 2px;")
        return line

    def _create_social_button(self, name: str, url: str) -> QPushButton:
        """Helper to create an accessible social media link button."""
        btn = QPushButton(name)
        btn.setObjectName("social_button")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setAccessibleName(f"فتح رابط حسابي على {name}")
        btn.clicked.connect(lambda checked=False, u=url: self._open_url(u))
        return btn

    def _open_url(self, url: str):
        """Opens the provided URL in the user's default web browser."""
        QDesktopServices.openUrl(QUrl(url))
        if hasattr(self.view_model, 'tts'):
            self.view_model.tts.speak("جاري فتح الرابط في المتصفح الافتراضي.", interrupt=True)
