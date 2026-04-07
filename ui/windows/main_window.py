from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    """
    Main application window. Currently a simple placeholder to test the integration.
    """
    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        
        self.setWindowTitle("IlmQuiz - Islamic Knowledge Challenge")
        self.resize(800, 600)
        
        # Setup central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create UI elements
        self.title_label = QLabel("IlmQuiz Engine Running Successfully!")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.test_button = QPushButton("Test Audio and TTS")
        self.test_button.clicked.connect(self._on_test_clicked)
        
        # Add elements to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.test_button)
        
        self.setCentralWidget(central_widget)

    def _on_test_clicked(self):
        """Test function to verify TTS and Audio services are working."""
        self.view_model.audio.play_sound("correct")
        self.view_model.read_text("Test successful. The engine is ready.", interrupt=True)
