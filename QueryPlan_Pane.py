from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt, QRectF

class QueryPlanPane(QWidget):
    '''
    This pane visually displays a top-down flowchart-style query plan
    using simple nodes and edges based on DuckDB's EXPLAIN output.
    '''
    def __init__(self):
        super().__init__()

        # Layout and title
        layout = QVBoxLayout(self)
        self.title = QLabel("Query Plan")
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)

        # Set minimum width to avoid cramped rendering
        self.setMinimumWidth(300)

        # Internal data for rendering
        self.nodes = []  # List of (id, label)
        self.edges = []  # List of (from_id, to_id)

    def display_plan(self, nodes, edges):
        '''
        Set the query plan data and trigger a repaint.
        '''
        self.nodes = nodes
        self.edges = edges
        self.update()

    def paintEvent(self, event):
        '''
        Called automatically by Qt to repaint the widget whenever needed.
        '''
        super().paintEvent(event)
        if not self.nodes:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw nodes
        pen = QPen(Qt.black)
        painter.setPen(pen)
        node_positions = {}

        x = self.width() // 2
        y_spacing = 120  # Vertical space between nodes

        for i, (node_id, label) in enumerate(self.nodes):
            y = 60 + i * y_spacing
            rect = QRectF(x - 80, y, 160, 50)  # Centered box

            # Draw box
            painter.drawRect(rect)

            # Adjust font
            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)

            # Draw label with ellipsis if too long
            elided = painter.fontMetrics().elidedText(label, Qt.ElideRight, rect.width() - 10)
            painter.drawText(rect, Qt.AlignCenter, elided)

            # Store center point of box for edge drawing
            node_positions[node_id] = (x, y + 25)

        # Draw edges (lines connecting nodes)
        for from_id, to_id in self.edges:
            if from_id in node_positions and to_id in node_positions:
                from_x, from_y = node_positions[from_id]
                to_x, to_y = node_positions[to_id]
                painter.drawLine(from_x, from_y + 25, to_x, to_y - 25)

def parse_duckdb_plan(plan_rows):
    '''
    Converts DuckDB's EXPLAIN output into graph nodes and edges for visualization.
    '''
    nodes = []
    edges = []
    stack = []

    for i, (line,) in enumerate(plan_rows):
        # Determine the indentation level
        indent = len(line) - len(line.lstrip("│├└─ "))
        label = line.strip("│├└─ ")
        node_id = f"n{i}"
        nodes.append((node_id, label))

        # Backtrack until the correct parent is found
        while stack and stack[-1][1] >= indent:
            stack.pop()

        # Add edge if a parent exists
        if stack:
            parent_id = stack[-1][0]
            edges.append((parent_id, node_id))

        # Push current node onto stack with its indent level
        stack.append((node_id, indent))

    return nodes, edges
