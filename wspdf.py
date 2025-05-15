import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow, QVBoxLayout, QWidget, QScrollArea, QLabel, QListWidget, QSplitter, QFileDialog, QAction, QToolBar, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize


class PDFViewer(QScrollArea):
    def __init__(self, parent=None, pdf_file=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.pdf_widget = QWidget()
        self.setWidget(self.pdf_widget)
        self.layout = QVBoxLayout(self.pdf_widget)
        self.page_label = None
        self.pdf_document = None
        self.pdf_file = pdf_file
        self.current_page = 0
        self.load_pdf(pdf_file)

    def load_pdf(self, pdf_file, page_number=0):
        """Load PDF and display the requested page."""
        self.pdf_document = fitz.open(pdf_file)
        self.current_page = page_number
        self.show_page(page_number)

    def show_page(self, page_number):
        """Render the given page number."""
        if self.pdf_document is not None:
            page = self.pdf_document.load_page(page_number)
            pix = page.get_pixmap()

            # Convert Pixmap to QImage
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)

            # Convert QImage to QPixmap
            pixmap = QPixmap.fromImage(img)

            if self.page_label:
                self.layout.removeWidget(self.page_label)
                self.page_label.deleteLater()

            self.page_label = QLabel(self)
            self.page_label.setPixmap(pixmap)
            self.layout.addWidget(self.page_label)

    def get_page_count(self):
        """Get total number of pages in the PDF."""
        if self.pdf_document:
            return self.pdf_document.page_count
        return 0

    def next_page(self):
        """Go to the next page."""
        if self.current_page < self.get_page_count() - 1:
            self.current_page += 1
            self.show_page(self.current_page)

    def previous_page(self):
        """Go to the previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About WSoft Reader")
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout(self)

        # About text with author information
        about_text = QLabel(
            "WSoft Reader\n\n"
            "A simple PDF viewer built with PyMuPDF.\n\n"
            "Authors: WSoft (wsoft.github.io)\n\n"
            "Version 1.0", self
        )
        layout.addWidget(about_text)

        # Close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)


class WSoftReader(QMainWindow):
    def __init__(self, pdf_file=None):
        super().__init__()
        self.setWindowTitle("WSoft Reader")
        self.setGeometry(100, 100, 1000, 700)

        # Set the application icon
        self.setWindowIcon(QIcon("icon.png"))  # Use the icon.png file

        # MDI Area to handle multiple PDFs
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)

        # Sidebar for pages (this will show pages for each open PDF)
        self.page_list = QListWidget()
        self.page_list.setFixedWidth(200)
        self.page_list.itemClicked.connect(self.on_page_selected)

        # Splitter to split MDI area and page list
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.mdi_area)
        splitter.addWidget(self.page_list)
        splitter.setSizes([800, 200])
        self.setCentralWidget(splitter)

        self.opened_pdfs = {}

        # Menu and Toolbar setup
        self.init_ui()

        # If a PDF file is passed in the arguments, open it
        if pdf_file:
            self.open_new_pdf(pdf_file)

    def init_ui(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')
        open_action = QAction('Open PDF', self)
        open_action.triggered.connect(self.open_pdf)
        file_menu.addAction(open_action)

        # Help menu with About option
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Toolbar below the menu
        toolbar = self.addToolBar('Main Toolbar')
        toolbar.setIconSize(QSize(16, 16))  # Set the icon size for the toolbar

        # Toolbar Actions
        open_toolbar_action = QAction('Open PDF', self)
        open_toolbar_action.triggered.connect(self.open_pdf)
        toolbar.addAction(open_toolbar_action)

        next_page_action = QAction('Next Page', self)
        next_page_action.triggered.connect(self.next_page)
        toolbar.addAction(next_page_action)

        previous_page_action = QAction('Previous Page', self)
        previous_page_action.triggered.connect(self.previous_page)
        toolbar.addAction(previous_page_action)

    def open_pdf(self):
        """Open PDF file and display it in MDI area."""
        file_dialog = QFileDialog(self)
        pdf_file, _ = file_dialog.getOpenFileName(self, 'Open PDF', '', 'PDF Files (*.pdf)')

        if pdf_file:
            self.open_new_pdf(pdf_file)

    def open_new_pdf(self, pdf_file):
        """Open a new PDF in a new MDI subwindow."""
        viewer = PDFViewer(self, pdf_file)
        sub_window = QMdiSubWindow()
        sub_window.setWidget(viewer)
        sub_window.setWindowTitle(pdf_file)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

        # Store the PDF viewer for later use
        self.opened_pdfs[pdf_file] = viewer

        # Update page list for this PDF
        self.update_page_list(pdf_file)

    def update_page_list(self, pdf_file):
        """Update the list of pages in the sidebar for the given PDF."""
        viewer = self.opened_pdfs.get(pdf_file)
        if viewer:
            total_pages = viewer.get_page_count()
            for i in range(total_pages):
                item_text = f"{pdf_file} - Page {i + 1}"
                if not any(item.text() == item_text for item in self.page_list.findItems("", Qt.MatchContains)):
                    self.page_list.addItem(item_text)

    def on_page_selected(self, item):
        """Change the current page when the user selects a page from the sidebar."""
        # Extract PDF file name and page number from the item
        text = item.text()
        pdf_file, page_info = text.split(" - ")
        page_number = int(page_info.split(" ")[1]) - 1  # Get page number (0-indexed)

        # Set the viewer to the selected PDF and page
        viewer = self.opened_pdfs.get(pdf_file)
        if viewer:
            viewer.show_page(page_number)

    def next_page(self):
        """Switch to the next page of the current active PDF."""
        active_sub_window = self.mdi_area.activeSubWindow()
        if active_sub_window:
            viewer = active_sub_window.widget()
            viewer.next_page()

    def previous_page(self):
        """Switch to the previous page of the current active PDF."""
        active_sub_window = self.mdi_area.activeSubWindow()
        if active_sub_window:
            viewer = active_sub_window.widget()
            viewer.previous_page()

    def show_about(self):
        """Display the About dialog."""
        dialog = AboutDialog()
        dialog.exec_()


if __name__ == '__main__':
    # Check if arguments are passed (PDF file path)
    pdf_file = None
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]

    app = QApplication(sys.argv)
    window = WSoftReader(pdf_file)
    window.show()
    sys.exit(app.exec_())
