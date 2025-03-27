def get_application_style():
    """Return the stylesheet for the application."""
    # Base styles for window and widgets
    base_styles = """
        QMainWindow, QWidget {
            background-color: #2D2D30;
            color: #E1E1E1;
        }
    """

    # Table widget styles
    table_styles = """
        QTableWidget {
            background-color: transparent;
            gridline-color: #3E3E42;
            border: 1px solid #3E3E42;
            border-radius: 4px;
            padding: 2px;
        }
        QTableWidget::item {
            padding: 6px;
            border-bottom: 1px solid #333337;
        }
        QTableWidget::item:selected {
            background-color: #007ACC;
            color: white;
        }
        QHeaderView::section {
            background-color: #333337;
            color: #E1E1E1;
            padding: 8px;
            border: 0px;
            font-weight: bold;
            border-right: 1px solid #3E3E42;
            border-bottom: 1px solid #3E3E42;
        }
        QTableCornerButton::section {
            background-color: #333337;
            border: 0px;
            border-right: 1px solid #3E3E42;
            border-bottom: 1px solid #3E3E42;
        }
    """

    # Button styles with disabled state
    button_styles = """
        QPushButton {
            background-color: #0078D7;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #1C86E0;
        }
        QPushButton:pressed {
            background-color: #0067C0;
        }
        QPushButton:disabled {
            background-color: #4D4D4D;
            color: #9D9D9D;
        }
        QPushButton#stopButton {
            background-color: #E74C3C;
        }
        QPushButton#stopButton:hover {
            background-color: #FF5A49;
        }
        QPushButton#stopButton:disabled {
            background-color: #7D4D4D;
            color: #9D9D9D;
        }
        QPushButton#deleteButton {
            background-color: #7D3C98;
        }
        QPushButton#deleteButton:hover {
            background-color: #913EB1;
        }
        QPushButton#deleteButton:disabled {
            background-color: #5D4D5D;
            color: #9D9D9D;
        }
    """

    # Input field styles
    input_styles = """
        QTextEdit, QLineEdit {
            background-color: #252526;
            border: 1px solid #3E3E42;
            border-radius: 4px;
            color: #E1E1E1;
            padding: 6px;
            selection-background-color: #007ACC;
        }
        QLineEdit#searchBox {
            padding-left: 24px;
            border: 1px solid #3E3E42;
            background-color: #252526;
        }
    """

    # Tab styles
    tab_styles = """
        QTabWidget::pane {
            border: 1px solid #3E3E42;
            border-radius: 4px;
            top: -1px;
        }
        QTabBar::tab {
            background-color: #333337;
            color: #E1E1E1;
            border: 1px solid #3E3E42;
            padding: 10px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #007ACC;
            border-bottom: none;
            font-weight: bold;
        }
        QTabBar::tab:!selected:hover {
            background-color: #3F3F46;
        }
    """

    # Status bar and tool styles
    status_tool_styles = """
        QStatusBar {
            background-color: #1E1E1E;
            color: #E1E1E1;
            border-top: 1px solid #3E3E42;
        }
        QStatusBar::item {
            border: none;
        }
        QToolButton {
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }
        QToolButton:hover {
            background-color: #3E3E42;
        }
    """

    # Splitter and scrollbar styles
    scrollbar_styles = """
        QSplitter::handle {
            background-color: #3E3E42;
        }
        QSplitter::handle:hover {
            background-color: #007ACC;
        }
        QScrollBar:vertical {
            border: none;
            background: #2D2D30;
            width: 14px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #3E3E42;
            min-height: 30px;
            border-radius: 7px;
        }
        QScrollBar::handle:vertical:hover {
            background: #007ACC;
        }
    """

    # Frame styles
    frame_styles = """
        QFrame {
            border: 1px solid #3E3E42;
            border-radius: 4px;
        }
    """

    # Combine all styles
    return (
        base_styles +
        table_styles +
        button_styles +
        input_styles +
        tab_styles +
        status_tool_styles +
        scrollbar_styles +
        frame_styles
    )
