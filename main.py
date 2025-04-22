# Import sys to access command line arguments
import sys
# Import duckdb to run SQL queries
import duckdb
# Widgets for the GUI layout
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt

# Import the panes for the GUI
from Shell_Pane import ShellPane # Where the user can execute their SQL query.
from QueryPlan_Pane import QueryPlanPane # Pane that shows the query plan flowchart.
from LineageExplorer_Pane import LineageExplorerPane # Pane that shows the data lineage (orgins of pieces of output)

# The path to the file with the database. In this case, ingredients.csv from A2
database_path = "ingredients.csv"


class SQLStepper(QWidget):
    # This sets up the main application window that hosts the shell, query plan, and lineage explorer panes.
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLStepper")

        # Set up the layout for the window
        layout = QHBoxLayout(self)

        # Initialize all the panes
        self.shell = ShellPane()
        self.plan = QueryPlanPane()
        self.lineage = LineageExplorerPane()

        # Connect shell signal to query handler
        self.shell.query_submitted.connect(self.handle_query_submission)

        # Create a splitter so all the panes can fit in the main window.
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.shell)
        splitter.addWidget(self.plan)
        splitter.addWidget(self.lineage)

        # After setting up the splitter, add it to the main layout and apply it to the main window
        layout.addWidget(splitter)
        self.setLayout(layout)

    def handle_query_submission(self, query):
        '''
        Triggered whenever the user submits a query from the shell window
        Upates all three panes based on the query result.
        '''
        #print("Received query from shell:")
        #print(query)

        # Get's the path to the database. In this case, it uses the ingredients.csv file from A2
        csv_path = "ingredients.csv"

        # Call the execute query method in the shell and store it so it can be used in the other panes.
        headers, rows = self.shell.execute_query_on_csv(database_path, query)

        # Call the display_results method from the shell file to display the output table of the query.
        self.shell.display_result(headers, rows)
        # Call the display_lineage method from the lineage explorer file to display the lineage (origins) of each piece of output data.
        self.lineage.display_lineage(headers=headers, input_rows=rows)
        # Build a flowchart from the query and database
        nodes, edges = build_flowchart_from_plan(query, database_path)
        self.plan.display_plan(nodes, edges)


def build_flowchart_from_plan(query, database_path):
    '''
    Builds a flowchart from parsed nodes and edges from the query.
    '''
    # Connect to DuckDB database
    con = duckdb.connect()
    con.execute(f"""
        CREATE OR REPLACE TABLE ingredients AS
        SELECT * FROM read_csv_auto('{database_path}')
    """)
    # Get the execution plan for the query
    con.execute(f"EXPLAIN {query}")
    # Fetch all the lines of the output
    plan_rows = con.fetchall()
    # Close the connection to duckdb once finished
    con.close()
    # Parse the rows into a format that can be used in the flowchart
    return parse_duckdb_plan(plan_rows)


def parse_duckdb_plan(plan_rows):
    '''
    Takes the DuckDB explain output and puts it into a graph structure
    that can be used for creating the top down flow chart in the query plan pane.
    '''
    # The individual parts of the query
    nodes = []
    # The directed edges that show the relationship between the nodes
    edges = []
    stack = []

    # Loop through each line in the output and determine the indentation by stripping away the symbols
        # and creating unique ids for each node.
    for i, (line,) in enumerate(plan_rows):
        indent = len(line) - len(line.lstrip("│├└─ "))
        label = line.strip("│├└─ ")
        node_id = f"n{i}"
        nodes.append((node_id, label))

        # Pop the stack until we find the correct parent
        while stack and stack[-1][1] >= indent:
            stack.pop()
        # Create an edge between the parent and node
        if stack:
            parent_id = stack[-1][0]
            edges.append((parent_id, node_id))
        # Push the node to the stack
        stack.append((node_id, indent))

    return nodes, edges


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SQLStepper()
    window.resize(1200, 600)
    window.show()
    sys.exit(app.exec())
