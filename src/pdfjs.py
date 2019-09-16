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
from aqt import mw
from aqt.qt import *
from aqt.utils import (
    showInfo,
    tooltip
)
from aqt.reviewer import Reviewer
from aqt.mediasrv import RequestHandler
from aqt.editor import Editor

from . import card_layout
from . import settings


def gc(arg, fail=False):
    return mw.addonManager.getConfig(__name__).get(arg, fail)


addon_path = os.path.dirname(__file__)
addonfoldername = os.path.basename(addon_path)
addondir = os.path.join(addon_path)
regex = r"(web.*)"
mw.addonManager.setWebExports(__name__, regex)
web_path = "/_addons/%s/web/" % addonfoldername


class NewDialog(QDialog):
    def __init__(self, parent, url, win_title):
        super(NewDialog, self).__init__(parent)
        self.url = url
        self.setWindowTitle(win_title)
        try:
            w, h = mw.pm.profile["144970292_dimensions"]
            w, h = int(w), int(h)
        except:
            w, h = 790, 1100
        self.resize(w, h)
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
        self.exit_shortcut.activated.connect(self.onReject)

    def onReject(self):
        mw.pm.profile["144970292_dimensions"] = (self.width(), self.height())
        self.reject()

    def closeEvent(self, evnt):
        mw.pm.profile["144970292_dimensions"] = (self.width(), self.height())

    def load_finished(self, success):
        if success:
            self.web.show()
        else:
            tooltip('page failed to load')


def open_pdf_in_internal_viewer(file, page):
    filename_page_fmt = """?file=%%2F%s%s#page=%s""" % ("_pdfjspath/", file, page)
    win_title = 'Anki - pdf viewer'
    url = "http://127.0.0.1:%d/_addons/%s/web/%s%s" % (
          mw.mediaServer.getPort(), addonfoldername, "pdfjs/web/viewer.html", filename_page_fmt)
    d = NewDialog(mw, url, win_title)
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


# from lovac42's Anki Fanfare/main.py from https://github.com/lovac42/Fanfare
# Replace /user/collection.media folder with actual addon path
def _redirectWebExports(self, path, _old):
    targetPath = os.path.join(os.getcwd(), "_pdfjspath")
    pdf_folder_path = gc("pdf_folder_paths", "")
    if path.startswith(targetPath) and pdf_folder_path:
        targetLength = len(targetPath)+1
        return os.path.join(pdf_folder_path, path[targetLength:])
    return _old(self, path)
RequestHandler._redirectWebExports = wrap(RequestHandler._redirectWebExports,
                                          _redirectWebExports, 'around')


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
