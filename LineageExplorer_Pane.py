from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt

class LineageExplorerPane(QWidget):
    '''
    Displays the lineage of each output row by showing which input row
    contributed to it. Used for visualizing data provenance.
    '''
    def __init__(self):
        super().__init__()

        # Layout container for the widget
        layout = QVBoxLayout(self)

        # Title label
        self.title = QLabel("Lineage Explorer")
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)

        # Read-only text area for displaying lineage info
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

    def display_lineage(self, headers, input_rows):
        '''
        Given a list of headers and input rows (query result),
        display each output row and its corresponding input row values.
        '''
        self.text_area.clear()

        # Show a message if there's no data
        if not input_rows:
            self.text_area.setText("No lineage available.")
            return

        # Show a simple mapping from output to input row
        for idx, row in enumerate(input_rows):
            row_data = ", ".join(f"{h}: {v}" for h, v in zip(headers, row))
            self.text_area.append(f"Output Row {idx} <- Input Row: {row_data}\n")
