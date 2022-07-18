from aqt.qt import (
    QDialog,
    QDialogButtonBox,
    Qt,
    QVBoxLayout,
    QTextBrowser,
    qconnect,
    qtmajor,
)
from aqt.utils import openLink

from aqt.webview import AnkiWebView



class InfoDialog(QDialog):
    def __init__(self, parent, window_title, content):
        QDialog.__init__(self, parent, Qt.WindowType.Window)
        self.parent = parent
        self.setWindowTitle(window_title)
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.te = QTextBrowser()
        self.te.setOpenLinks(False)  # TextBrowser should not open links in its window - https://doc.qt.io/qt-6/qtextbrowser.html#openLinks-prop
        self.te.anchorClicked.connect(self.open_links)  # I need no_bundled_libs() ....
        self.te.setHtml(content)
        self.te.setReadOnly(True)
        self.vbox.addWidget(self.te)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        qconnect(self.button_box.button(QDialogButtonBox.StandardButton.Ok).clicked, self.accept)
        self.vbox.addWidget(self.button_box)

        self.setLayout(self.vbox)
        self.resize(950, 480)
    
    def open_links(self, link):
        print(link)
        openLink(link)

