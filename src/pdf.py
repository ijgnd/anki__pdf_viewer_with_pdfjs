"""
anki-addon: pdf viewer (with mozilla's pdfjs)

Copyright (c) 2019 ignd
          (c) 2018 lovac42
          (c) 2019 arthurmilchior
          (c) Ankitects Pty Ltd and contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


This add-on uses mozilla's pdfjs which uses a license other than AGPL3, see
the comments on top of the files in the folder web/pdfjs.
"""

import os
import re
from pprint import pprint as pp  # noqa

from anki.hooks import addHook, wrap
from anki.utils import (
    stripHTML,
)
from .anki_version_detection import anki_point_version
from .config import gc

from aqt import mw
from aqt.qt import *
from aqt.utils import (
    restoreGeom,
    saveGeom,
    showInfo,
    tooltip,
)
from aqt.previewer import Previewer
from aqt.reviewer import Reviewer
import aqt.mediasrv as mediasrv


addon_path = os.path.dirname(__file__)
addonfoldername = os.path.basename(addon_path)
addondir = os.path.join(addon_path)
regex = r"(web[/\\].*)"
mw.addonManager.setWebExports(__name__, regex)
web_path = "/_addons/%s/web/" % addonfoldername


class PdfJsViewer(QDialog):
    def __init__(self, parent, url, win_title):
        super(PdfJsViewer, self).__init__(parent)
        if anki_point_version < 45:
            mw.setupDialogGC(self)
        else:
            mw.garbage_collect_on_dialog_finish(self)
        self.url = url
        self.setWindowTitle(win_title)
        restoreGeom(self, "319501851")
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        self.web = QWebEngineView()
        self.web.title = "pdfjs"
        mainLayout.addWidget(self.web)
        QMetaObject.connectSlotsByName(self)
        self.web.load(QUrl(self.url))
        self.web.show()
        self.web.loadFinished.connect(self.load_finished)
        # self.web.setFocus()
        self.exit_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.exit_shortcut.activated.connect(self.reject)

    def reject(self):
        saveGeom(self, "319501851")
        QDialog.reject(self)

    def closeEvent(self, evnt):
        saveGeom(self, "319501851")

    def load_finished(self, success):
        if success:
            self.web.show()
        else:
            tooltip('page failed to load')


class ChromiumPdfViewerWindow(QDialog):
    def __init__(self, parent, url, win_title):
        super(ChromiumPdfViewerWindow, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle(win_title)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        self.setGeometry(0, 28, 1000, 750)
        self.webview = QWebEngineView()
        self.webview.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.webview.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        mainLayout.addWidget(self.webview)
        url_as_qurl = QUrl(url)
        self.webview.load(url_as_qurl)

        # "#page=" are ignored in pyqt5
        # https://stackoverflow.com/questions/60560583/open-pdf-at-specific-page-with-qt-webengineview
        # apparently a bug in qt5: https://bugreports.qt.io/browse/QTBUG-86152
        # this pyqt6 minimal external program works: https://python-forum.io/thread-36741-post-155217.html#pid155217
        # this pyqt5 minimal external program does not work: https://python-forum.io/thread-36741-post-155207.html#pid155207
        # so I need a workaround for pyqt5
        # inspired by https://stackoverflow.com/questions/60560583/open-pdf-at-specific-page-with-qt-webengineview
        # workaround for qt5 to open specific pages
        self.webview.loadFinished.connect(self.load_finished)
        self.page_num = None
        if "#page=" in url:
            self.page_num = url.split("#page=")[1]
            try:
                int(self.page_num)
            except:
                self.page_num = None
    
    def go_to_page(self):
        # this solution was suggested by eyllanesc in 2020-03. 
        # https://stackoverflow.com/questions/60560583/open-pdf-at-specific-page-with-qt-webengineview
        # it doesn't work for me (and neither in 2021-03 for
        # https://forum.qt.io/topic/126003/qwebengineview-to-view-local-pdf-at-certain-page
        # I get:
        # Qt critical: Uncaught TypeError: Cannot read property 'viewport_' of null '1,'
        if self.page_num:
            self.webview.page().runJavaScript(f"window.viewer.viewport_.goToPage({self.page_num})")
    
    def load_finished(self):
        # if success and self.page_num:
        t = QTimer(self.parent)
        t.timeout.connect(self.go_to_page)  # type: ignore
        t.setSingleShot(True)
        t.start(1000)   
        self.go_to_page()


handledfile = None


def open_pdf_in_internal_viewer__with_pdfjs(file, page):
    fmt = f"?file=/_pdfjspath/{file}#page={page}"
    win_title = 'Anki - pdf viewer'
    port = mw.mediaServer.getPort()
    if gc("pdf_js_version_used") == "mid_2021":
        url = f"http://127.0.0.1:{port}/_addons/{addonfoldername}/web/pdfjs_mid_2021/web/viewer.html{fmt}"
    else:
        # the regular version from https://github.com/mozilla/pdf.js/releases/download/v2.14.305/pdfjs-2.14.305-dist.zip
        # does not work with anki 2.1.49 in 2022-07-13
        url = f"http://127.0.0.1:{port}/_addons/{addonfoldername}/web/pdfjs_2022-05-14__v2.14.305_legacy/web/viewer.html{fmt}"
    d = PdfJsViewer(mw, url, win_title)
    d.show()


def open_pdf_in_internal_viewer__with_chromium_pdf(file, page):
    win_title = 'Anki - pdf viewer'
    port = mw.mediaServer.getPort()
    # url = f"{file}#page={page}"  # for pdfs in the media folder
    url = f"http://127.0.0.1:{port}/_pdfjspath/{file}#page={page}"
    d = ChromiumPdfViewerWindow(mw, url, win_title)
    d.show()


def open_pdf_in_internal_viewer_helper(file, page):
    global handledfile
    handledfile = file
    if gc("use pdfjs to show pdfs", False):
        open_pdf_in_internal_viewer__with_pdfjs(file, page)
    else:
        open_pdf_in_internal_viewer__with_chromium_pdf(file, page)
mw.pdf_folder_path = gc("pdf_folder_paths")
mw.open_pdf_in_internal_viewer_helper = open_pdf_in_internal_viewer_helper


def basic_check_filefield(file, showinfos):
    targetfile = os.path.join(gc("pdf_folder_paths"), file)
    if not os.path.isfile(targetfile):
        nemsg = ("The file '%s' does not exist in the folder '%s'. Maybe "
                 "the file is missing, maybe there's a typo or maybe "
                 "there's too much else in the field '%s'. Aborting ..."
                 "\nAlso see the description of the add-on "
                 "''anki pdf viewer (pdfjs)' on ankiweb." % (
                  file, gc("pdf_folder_paths"), gc("field_for_filename"))
                 )
        if showinfos:
            showInfo(nemsg)
        return
    if file.startswith("file:/"):
        vmsg = ("illegal values in field '%s'. See description of the add-on "
                "'anki pdf viewer (pdfjs)' on Ankiweb. Aborting..." % 
                gc("field_for_filename", "")
                )
        if showinfos:
            showInfo(vmsg)
        return
    return True


def myLinkHandler(self, url, _old):
    if url.startswith("pdfjs319501851"):
        file, page = url.replace("pdfjs319501851", "").split("319501851")
        page = re.sub(r"\D", "", page)
        if basic_check_filefield(file, True):
            open_pdf_in_internal_viewer_helper(file, page)
    else:    
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")
Previewer._on_bridge_cmd = wrap(Previewer._on_bridge_cmd, myLinkHandler, "around")


if anki_point_version <= 49:
    def _redirectWebExports(path, _old):
        global handledfile
        pdf_folder_path = gc("pdf_folder_paths", "")
        if path.startswith("_pdfjspath") and pdf_folder_path:
            directory, filename = os.path.split(handledfile)
            # handledfile = None  # this breaks open_pdf_in_internal_viewer__with_chromium_pdf: for some reason _redirectWebExports is called twice
            if not directory:
                justfilename = path[11:]
                return pdf_folder_path, justfilename
            else:
                if gc("open pdfs from other paths than the default path"):
                    return directory, filename
        else:
            return _old(path)
    mediasrv._redirectWebExports = wrap(mediasrv._redirectWebExports,
                                              _redirectWebExports, 'around')


if anki_point_version >= 50:
    # LocalFileRequest takes two args:
        # base folder, eg media folder
        # path to file relative to root folder
    from aqt.mediasrv import LocalFileRequest

    def _extract_pdf_request(path, _old):
        global handledfile
        pdf_folder_path = gc("pdf_folder_paths", "")
        if path.startswith("_pdfjspath") and pdf_folder_path:
            directory, filename = os.path.split(handledfile)
            # handledfile = None  # this breaks open_pdf_in_internal_viewer__with_chromium_pdf: for some reason _redirectWebExports is called twice
            if not directory:
                justfilename = path[11:]
                return LocalFileRequest(root=pdf_folder_path, path=justfilename)
            else:
                if gc("open pdfs from other paths than the default path"):
                    return LocalFileRequest(root=pdf_folder_path, path=justfilename)
        else:
            return _old(path)

    mediasrv._extract_addon_request = wrap(mediasrv._extract_addon_request,
                                                _extract_pdf_request, 'around')


def myhelper(editor, menu):
    filefld = [f["ord"] for f in editor.note.model()['flds'] if f['name'] == gc("field_for_filename")]
    if not filefld:
        return
    file = stripHTML(editor.note.fields[filefld[0]])
    pagefld = [f["ord"] for f in editor.note.model()['flds'] if f['name'] == gc("field_for_page")]
    page = ""
    if pagefld:
        page = stripHTML(editor.note.fields[pagefld[0]])
    if basic_check_filefield(file, False):
        a = menu.addAction("open pdf")
        a.triggered.connect(lambda _, f=file, p=page: open_pdf_in_internal_viewer_helper(f, p))


def add_to_context(view, menu):
    e = view.editor
    field = e.currentField
    if field:
        e.saveNow(lambda ed=e, m=menu: myhelper(ed, m))
    else:
        myhelper(e, menu)
addHook("EditorWebView.contextMenuEvent", add_to_context)  # noqa
