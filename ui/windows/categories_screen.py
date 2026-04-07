from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, Signal

class CategoriesScreen(QWidget):
    """Screen displaying the main quiz categories with their descriptions."""
    
    category_selected = Signal(int)

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self._setup_ui()

    def _setup_ui(self):
        # Main layout with some padding
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Main Title
        title_label = QLabel("اختر تصنيفاً لنبدأ التحدي")
        title_label.setObjectName("screen_title") # For specialized CSS
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Grid for categories
        grid_layout = QGridLayout()
        grid_layout.setSpacing(25)
        
        categories = self.view_model.get_categories()
        
        row, col = 0, 0
        for category in categories:
            # Create a 'Card' for each category
            card = QFrame()
            card.setObjectName("category_card")
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(10)

            # Category Name Button
            btn = QPushButton(category.arabic_name)
            btn.setObjectName("category_button")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, cid=category.id: self._on_category_clicked(cid))
            
            # Description Label
            desc_label = QLabel(category.description)
            desc_label.setObjectName("category_description")
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Add to card layout
            card_layout.addWidget(btn)
            card_layout.addWidget(desc_label)
            
            # Add card to the main grid
            grid_layout.addWidget(card, row, col)
            
            col += 1
            if col > 1: # 2 columns layout
                col = 0
                row += 1

        layout.addLayout(grid_layout)

    def _on_category_clicked(self, category_id: int):
        self.view_model.audio.play_sound("correct")
        self.category_selected.emit(category_id)
