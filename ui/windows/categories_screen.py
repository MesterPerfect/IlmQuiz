import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QFrame, QHBoxLayout
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QSize

class CategoriesScreen(QWidget):
    """Screen displaying the main quiz categories with icons and descriptions."""
    
    category_selected = Signal(int)
    settings_requested = Signal()
    stats_requested = Signal()
    about_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        # Map category IDs to their respective SVG icons
        self.icon_mapping = {
            1: "tafseer.svg",
            2: "akida.svg",
            3: "hadith.svg",
            4: "figh.svg",
            5: "history.svg",
            6: "arabia.svg"
        }
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Create a header layout for the title and settings button
        header_layout = QHBoxLayout()

        # Settings Button
        self.settings_btn = QPushButton("الإعدادات")
        self.settings_btn.setObjectName("back_button") # Reusing the style
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.settings_requested.emit)

        # About Button
        self.about_btn = QPushButton("حول البرنامج")
        self.about_btn.setObjectName("back_button") # تم التعديل
        self.about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.about_btn.clicked.connect(self.about_requested.emit)

        # Stats Button
        self.stats_btn = QPushButton("الإحصائيات")
        self.stats_btn.setObjectName("back_button")
        self.stats_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stats_btn.clicked.connect(self.stats_requested.emit)

        title_label = QLabel("اختر تصنيفاً لنبدأ التحدي")
        title_label.setObjectName("screen_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        header_layout.addWidget(self.settings_btn)
        header_layout.addWidget(self.about_btn)
        header_layout.addWidget(self.stats_btn)
        header_layout.addWidget(title_label, 1)
        layout.addLayout(header_layout)

        layout.addWidget(title_label)



        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        categories = self.view_model.get_categories()
        
        row, col = 0, 0
        for category in categories:
            card = QFrame()
            card.setObjectName("category_card")
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Icon Label
            icon_label = QLabel()
            icon_label.setObjectName("category_icon")
            icon_name = self.icon_mapping.get(category.id, "default.svg")
            icon_path = os.path.join("assets", "icons", icon_name)
            
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                # Scale the SVG to a suitable size (e.g., 80x80)
                icon_label.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Category Button
            btn = QPushButton(category.arabic_name)
            btn.setObjectName("category_button")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Link the description to the button for screen readers
            btn.setAccessibleDescription(category.description)
            btn.clicked.connect(lambda checked=False, cid=category.id: self._on_category_clicked(cid))
            
            # Description
            desc_label = QLabel(category.description)
            desc_label.setObjectName("category_description")
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Assembly
            card_layout.addWidget(icon_label)
            card_layout.addWidget(btn)
            card_layout.addWidget(desc_label)
            
            grid_layout.addWidget(card, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addLayout(grid_layout)

    def _on_category_clicked(self, category_id: int):
        self.view_model.audio.play_sound("correct")
        self.category_selected.emit(category_id)
