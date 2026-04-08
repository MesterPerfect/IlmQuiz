from PySide6.QtWidgets import QMainWindow, QStackedWidget
from .categories_screen import CategoriesScreen
from .topics_screen import TopicsScreen

class MainWindow(QMainWindow):
    """Main application window using QStackedWidget to manage screens."""
    
    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        
        self.setWindowTitle("IlmQuiz - Islamic Knowledge Challenge")
        self.resize(900, 700) # Slightly larger default size
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self._init_screens()

    def _init_screens(self):
        # Initialize Screens
        self.categories_screen = CategoriesScreen(self.view_model)
        self.topics_screen = TopicsScreen(self.view_model)
        
        # Connect Signals
        self.categories_screen.category_selected.connect(self._on_category_selected)
        self.topics_screen.back_requested.connect(self._show_categories_screen)
        self.topics_screen.topic_selected.connect(self._on_topic_selected)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(self.categories_screen)
        self.stacked_widget.addWidget(self.topics_screen)
        
        # Set initial screen
        self._show_categories_screen()

    def _show_categories_screen(self):
        self.stacked_widget.setCurrentWidget(self.categories_screen)
        self.view_model.read_text("شاشة التصنيفات", interrupt=True)

    def _on_category_selected(self, category_id: int):
        self.topics_screen.load_topics(category_id)
        self.stacked_widget.setCurrentWidget(self.topics_screen)
        self.view_model.read_text("شاشة المواضيع. اختر مستوى الصعوبة ثم اختر الموضوع.", interrupt=True)

    def _on_topic_selected(self, topic_id: int, level: int):
        # TODO: Transition to the Game Screen
        self.view_model.read_text(f"تم اختيار الموضوع. جاري تحميل الأسئلة.", interrupt=True)
        print(f"Starting game for topic {topic_id} at level {level}")
