from qtpy.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLabel, QWidget


class ToggleWidgetExample(QWidget):
    def __init__(self):
        super().__init__()

        # Create the main layout
        self.main_layout = QVBoxLayout()

        # Create the two widgets
        self.widget1 = QLabel("This is Widget 1")
        self.widget2 = QLabel("This is Widget 2")

        # Add the first widget to the layout
        self.main_layout.addWidget(self.widget1)

        # Create a button to toggle between widgets
        self.toggle_button = QPushButton("Toggle Widget")
        self.toggle_button.clicked.connect(self.toggle_widget)
        self.main_layout.addWidget(self.toggle_button)

        self.setLayout(self.main_layout)

        # Keep track of the currently displayed widget
        self.current_widget = self.widget1

    def toggle_widget(self):
        # Remove the current widget
        self.main_layout.removeWidget(self.current_widget)
        self.current_widget.hide()

        # Toggle to the other widget
        if self.current_widget == self.widget1:
            self.current_widget = self.widget2
        else:
            self.current_widget = self.widget1

        # Add the new widget to the layout
        self.main_layout.insertWidget(0, self.current_widget)
        self.current_widget.show()


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = ToggleWidgetExample()
    window.show()
    app.exec_()
