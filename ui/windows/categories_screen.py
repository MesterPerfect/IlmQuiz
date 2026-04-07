from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal

class CategoriesScreen(QWidget):
    """Screen displaying the main quiz categories."""
    
    category_selected = Signal(int)

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Choose a Category")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; margin-bottom: 20px;")
        layout.addWidget(title_label)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        categories = self.view_model.get_categories()
        
        row, col = 0, 0
        for category in categories:
            btn = QPushButton(category.arabic_name)
            # Use a lambda to pass the category ID when clicked
            btn.clicked.connect(lambda checked=False, cid=category.id: self._on_category_clicked(cid))
            
            grid_layout.addWidget(btn, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addLayout(grid_layout)

    def _on_category_clicked(self, category_id: int):
        self.view_model.audio.play_sound("correct")
        self.category_selected.emit(category_id)
