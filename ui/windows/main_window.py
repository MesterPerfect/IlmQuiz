from PySide6.QtWidgets import QMainWindow, QStackedWidget
from .categories_screen import CategoriesScreen

class MainWindow(QMainWindow):
    """Main application window using QStackedWidget to manage screens."""
    
    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        
        self.setWindowTitle("IlmQuiz - Islamic Knowledge Challenge")
        self.resize(800, 600)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self._init_screens()

    def _init_screens(self):
        # Initialize Categories Screen
        self.categories_screen = CategoriesScreen(self.view_model)
        self.categories_screen.category_selected.connect(self._on_category_selected)
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.categories_screen)
        
        # Set initial screen
        self.stacked_widget.setCurrentWidget(self.categories_screen)

    def _on_category_selected(self, category_id: int):
        # TODO: Switch to Topics screen and pass the category_id
        self.view_model.read_text(f"Category {category_id} selected.", interrupt=True)
        print(f"Transitioning to topics for category {category_id}")
