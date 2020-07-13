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
import io
import re
from pprint import pprint as pp

from anki.hooks import addHook, wrap
from anki.utils import (
    stripHTML
)
from anki import version as anki_version
_, _, pointversion = anki_version.split(".")
pointversion = int(pointversion)

from aqt import mw
from aqt.qt import *
from aqt.utils import (
    restoreGeom,
    saveGeom,
    showInfo,
    tooltip
)
if pointversion >= 24:
    from aqt.previewer import Previewer
from aqt.reviewer import Reviewer
import aqt.mediasrv as mediasrv
from aqt.editor import Editor

from . import card_layout
from . import settings


def gc(arg, fail=False):
    try:
        out = mw.addonManager.getConfig(__name__).get(arg, fail)
    except:
        return None
    else:
        return out


from anki import version as anki_version
_, _, point = anki_version.split(".")
pointversion = int(point)


addon_path = os.path.dirname(__file__)
addonfoldername = os.path.basename(addon_path)
addondir = os.path.join(addon_path)
regex = r"(web[/\\].*)"
mw.addonManager.setWebExports(__name__, regex)
web_path = "/_addons/%s/web/" % addonfoldername


class PdfJsViewer(QDialog):
    def __init__(self, parent, url, win_title):
        super(PdfJsViewer, self).__init__(parent)
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
        self.exit_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
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


handledfile = None
def open_pdf_in_internal_viewer(file, page):
    global handledfile
    handledfile = file
    fmt = f"?file=%2F_pdfjspath/{file}#page={page}"
    win_title = 'Anki - pdf viewer'
    port = mw.mediaServer.getPort()
    url = f"http://127.0.0.1:{port}/_addons/{addonfoldername}/web/pdfjs/web/viewer.html{fmt}"
    d = PdfJsViewer(mw, url, win_title)
    d.show()


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
                gc("field_for_filename","")
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
            open_pdf_in_internal_viewer(file, page)
    else:
        _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")
if pointversion >= 24:
    Previewer._on_bridge_cmd = wrap(Previewer._on_bridge_cmd, myLinkHandler, "around")


# from lovac42's Anki Fanfare/main.py from https://github.com/lovac42/Fanfare
# Replace /user/collection.media folder with actual addon path
def _redirectWebExports(self, path, _old):
    targetPath = os.path.join(os.getcwd(), "_pdfjspath")
    pdf_folder_path = gc("pdf_folder_paths", "")
    if path.startswith(targetPath) and pdf_folder_path:
        targetLength = len(targetPath)+1
        return os.path.join(pdf_folder_path, path[targetLength:])
    return _old(self, path)
if pointversion < 28:
    mediasrv.RequestHandler._redirectWebExports = wrap(mediasrv.RequestHandler._redirectWebExports,
                                          _redirectWebExports, 'around')


def _redirectWebExportsNEW(path, _old):
    global handledfile
    pdf_folder_path = gc("pdf_folder_paths", "")
    if path.startswith("_pdfjspath") and pdf_folder_path:
        if handledfile:
            directory, filename = os.path.split(handledfile)
            if not directory:
                justfilename = path[11:]
                return pdf_folder_path, justfilename
            else:
                return directory, filename
    return _old(path)
if pointversion >= 28:
    mediasrv._redirectWebExports = wrap(mediasrv._redirectWebExports,
                                          _redirectWebExportsNEW, 'around')


def myhelper(editor, menu):
    filefld = [f["ord"] for f in editor.note.model()['flds'] if f['name'] == gc("field_for_filename")]
    if not filefld:
        return
    file = stripHTML(editor.note.fields[filefld[0]])
    pagefld = [f["ord"] for f in editor.note.model()['flds'] if f['name'] == gc("field_for_page")]
    if pagefld:
        page = stripHTML(editor.note.fields[pagefld[0]])
    if basic_check_filefield(file, False):
        a = menu.addAction("open pdf")
        a.triggered.connect(lambda _, f=file, p=page: open_pdf_in_internal_viewer(f, p))


def add_to_context(view, menu):
    e = view.editor
    field = e.currentField
    if field:
        e.saveNow(lambda ed=e, m=menu: myhelper(ed, m))
    else:
        myhelper(e, menu)
addHook("EditorWebView.contextMenuEvent", add_to_context)
