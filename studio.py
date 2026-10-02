import os
import subprocess
import sys

try:
    from PyQt6.QtCore import Qt, QRegularExpression, QSize, QRect, QPoint
    from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QPainter, QFileSystemModel
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QPushButton, QSplitter, QTreeView,
        QTabWidget, QMessageBox, QFrame, QFileDialog
    )
except ModuleNotFoundError as exc:
    raise SystemExit(
        "PyQt6 is required to run this IDE. Install it with: python3 -m pip install PyQt6"
    ) from exc

class UrdulangHighlighter(QSyntaxHighlighter):
    """Custom syntax highlighter for Urdulang keywords"""
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # Keyword Format (Cyan/Blue)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0463b1"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = ["rakho", "bol", "agar", "jab_tak", "kaam", "show_window", "aage", "dayen", "bayen"]
        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Comment Format (Green)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a9955"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression(r"#[^\n]*"), comment_format))

        # Number Format (Light Orange)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\b"), number_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QTextEdit):
    """Monospace code editor pane with syntax highlighting and line numbers"""
    def __init__(self):
        super().__init__()
        self.setFont(QFont("JetBrains Mono", 11))
        self.setStyleSheet("""
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: none;
            selection-background-color: #264f78;
        """)
        self.highlighter = UrdulangHighlighter(self.document())

        # Line number area setup
        self.line_number_area = LineNumberArea(self)

        self.document().blockCountChanged.connect(self.update_line_number_area_width)
        self.verticalScrollBar().valueChanged.connect(self.line_number_area.update)
        self.document().contentsChange.connect(self.update_line_number_area_contents)

        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        digits = 1
        max_val = max(1, self.document().blockCount())
        while max_val >= 10:
            max_val //= 10
            digits += 1
        space = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area_contents(self, rect, db, ds):
        self.line_number_area.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))

        cursor = self.cursorForPosition(QPoint(0, 0))
        block = cursor.block()
        block_number = block.blockNumber()
        top = self.cursorRect(cursor).top()
        bottom = top + self.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.setFont(self.font())
                painter.drawText(0, top, self.line_number_area.width() - 8, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            if block.isValid():
                cursor.setPosition(block.position())
                top = self.cursorRect(cursor).top()
                bottom = top + self.fontMetrics().height()
            else:
                top = bottom
                bottom = top
            block_number += 1


class UrdulangStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Urdulang--IDE")
        self.resize(1100, 750)
        self.project_dir = os.getcwd()

        # Apply Modern Dark Professional Palette
        self.setStyleSheet("""
            QMainWindow { background-color: #181818; }
            QSplitter::handle { background-color: #333333; }
            QTabWidget::pane { border: 1px solid #333333; background: #1e1e1e; }
            QTabBar::tab { background: #2d2d2d; color: #969696; padding: 8px 16px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
            QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-bottom: 2px solid #007acc; }
            QTreeView { background-color: #252526; color: #cccccc; border: none; font-size: 10pt; }
            QTreeView::item:selected { background-color: #37373d; color: white; }
            QPushButton { background-color: #0e639c; color: white; border: none; padding: 6px 14px; border-radius: 3px; font-weight: bold; font-size: 10pt; }
            QPushButton:hover { background-color: #1177bb; }
            QPushButton:pressed { background-color: #094771; }
        """)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Project actions
        toolbar = QFrame()
        toolbar.setFixedHeight(48)
        toolbar.setStyleSheet("background-color: #2d2d2d; border-bottom: 1px solid #333333;")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(10, 6, 10, 6)

        folder_btn = QPushButton("Open Folder")
        folder_btn.clicked.connect(self.open_folder)
        tb_layout.addWidget(folder_btn)

        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self.run_code)
        tb_layout.addWidget(run_btn)
        tb_layout.addStretch()

        main_layout.addWidget(toolbar)

        # 2. Main Splitter (Left: File Explorer, Right: Editor + Console)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        # File Explorer Sidebar
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.project_dir)
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(self.project_dir))
        # Hide extra columns like size, type
        for i in range(1, 4):
            self.file_tree.setColumnHidden(i, True)
        self.file_tree.doubleClicked.connect(self.open_file_from_tree)
        main_splitter.addWidget(self.file_tree)

        # Right Side Splitter (Editor on top, Console on bottom)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Tabs for multiple open scripts
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # Open default initial tab
        self.new_tab("script.urdu", "# Urdulang Professional Script\nrakho x = 1\njab_tak x <= 3 {\n    bol x\n    rakho x = x + 1\n}\n")
        right_splitter.addWidget(self.tabs)

        # Console Output Log
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("JetBrains Mono", 10))
        self.console.setStyleSheet("background-color: #111111; color: #4ec9b0; border: none; padding: 8px;")
        right_splitter.addWidget(self.console)

        right_splitter.setStretchFactor(0, 5)
        right_splitter.setStretchFactor(1, 1)
        right_splitter.setSizes([520, 130])
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([220, 880])

    def new_tab(self, title, content=""):
        editor = CodeEditor()
        editor.setPlainText(content)
        self.tabs.addTab(editor, title)
        self.tabs.setCurrentWidget(editor)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def open_file_from_tree(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path) and path.endswith(".urdu"):
            with open(path, "r") as f:
                content = f.read()
            self.new_tab(os.path.basename(path), content)

    def open_folder(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Open Folder", self.project_dir
        )
        if directory:
            self.project_dir = directory
            self.file_tree.setRootIndex(self.file_model.setRootPath(directory))

    def run_code(self):
        current_editor = self.tabs.currentWidget()
        if not current_editor:
            return

        # Save active content to temporary runtime file
        with open(os.path.join(self.project_dir, "script.urdu"), "w") as f:
            f.write(current_editor.toPlainText())

        self.console.clear()
        self.console.append(f"--- Executing ./urdulang script.urdu ---\n")

        try:
            result = subprocess.run(
                ["./urdulang", "script.urdu"],
                capture_output=True, text=True, timeout=5, cwd=self.project_dir
            )
            if result.stdout:
                self.console.append(result.stdout)
            if result.stderr:
                self.console.append(f"Runtime Error:\n{result.stderr}")
            self.console.append("\n--- Process Finished ---")
        except FileNotFoundError:
            QMessageBox.critical(self, "Compilation Error", "Binary './urdulang' nahi mila! Pehle terminal me 'gcc main.c -o urdulang -lraylib -lm -ldl -lpthread' run karein.")
        except subprocess.TimeoutExpired:
            QMessageBox.warning(self, "Infinite Loop", "Program time limit cross kar gaya (Infinite loop detected).")

if __name__ == "__main__":
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication(sys.argv)
    studio = UrdulangStudio()
    studio.show()
    sys.exit(app.exec())