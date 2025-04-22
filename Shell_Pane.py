from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QSizePolicy
)
from PySide6.QtCore import Signal

import duckdb
import pandas as pd

class ShellPane(QWidget):
    # Signal emitted when user submits a query
    query_submitted = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # SQL editor for user to type queries
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Enter your SQL query here please:")
        self.editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.editor.setMinimumHeight(100)
        layout.addWidget(self.editor)

        # Run button to trigger query submission
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.on_run_clicked)
        layout.addWidget(self.run_button)

        # Table to display query results
        self.result_table = QTableWidget()
        self.result_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.result_table)

        # Finalize layout
        self.setLayout(layout)

    def execute_query_on_csv(self, csv_path, query):
        """
        Reads CSV into DuckDB, executes the query, and returns results.
        Returns (headers, rows) if successful, or error message if failed.
        """
        try:
            df = pd.read_csv(csv_path)
            con = duckdb.connect()
            con.register("ingredients", df)
            result_df = con.execute(query).fetchdf()

            headers = result_df.columns.tolist()
            rows = result_df.values.tolist()

            return headers, rows
        except Exception as e:
            print("Error executing query:", e)
            return ["Error"], [[str(e)]]

    def on_run_clicked(self):
        """Triggered when Run button is clicked. Emits query signal."""
        sql_query = self.editor.toPlainText()
        self.query_submitted.emit(sql_query)

    def set_query_text(self, text: str):
        """Sets the SQL editor to the given query text."""
        self.editor.setPlainText(text)

    def clear(self):
        """Clears both the editor and result table."""
        self.editor.clear()
        self.result_table.clearContents()

    def display_result(self, headers, rows):
        """Displays query result (headers and rows) in the table widget."""
        self.result_table.clearContents()
        self.result_table.setRowCount(len(rows))
        self.result_table.setColumnCount(len(headers))
        self.result_table.setHorizontalHeaderLabels(headers)

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.result_table.setItem(row_idx, col_idx, item)

def get_query_plan(query: str, csv_path: str):
    """
    Helper function to return the EXPLAIN query plan from DuckDB.
    """
    con = duckdb.connect()
    con.execute(f"""
        CREATE OR REPLACE TABLE ingredients AS
        SELECT * FROM read_csv_auto('{csv_path}')
    """)
    explain_result = con.execute(f"EXPLAIN {query}").fetchall()
    con.close()

    # Join plan lines into a single string
    plan_text = "\n".join(row[0] for row in explain_result)
    return plan_text
