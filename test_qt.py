from PyQt6.QtWidgets import QApplication, QLabel;
import sys;

app = QApplication(sys.argv);
label = QLabel("Hello, World!");  # Create a label widget
label.show();

sys.exit(app.exec());  # Start the application event loop