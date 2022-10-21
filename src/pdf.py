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

# in 2022 only the pdfjs legacy version works. This is confirmed by  
# https://stackoverflow.com/a/48053017 that states:
# "as of Aug 2022, it may be necessary to use the legacy build of pdfjs to 
# keep things working with PyQt5. The stable build should work okay with PyQt6, though."

import base64
import os
from pprint import pprint as pp  # noqa

from .anki_version_detection import anki_point_version
from .config import gc

from anki.hooks import addHook, wrap
if anki_point_version <= 49:
    from anki.utils import stripHTML
else:
    from anki.utils import strip_html as stripHTML

import aqt
from aqt import mw
if anki_point_version >= 55:
    from aqt import colors
from aqt.qt import *
from aqt.theme import theme_manager
from aqt.utils import (
    restoreGeom,
    saveGeom,
    showInfo,
    tooltip,
)
from aqt.previewer import Previewer
from aqt.reviewer import Reviewer
from aqt.webview import AnkiWebPage
import aqt.mediasrv as mediasrv

from .copied.helpers import check_string_for_existing_file
from .window_move import move_window


addon_path = os.path.dirname(__file__)
addonfoldername = os.path.basename(addon_path)
addondir = os.path.join(addon_path)
regex = r"(web[/\\].*)"
mw.addonManager.setWebExports(__name__, regex)
web_path = "/_addons/%s/web/" % addonfoldername
       

def search_in_browser(file_name, page):
    # file_name already has .pdf extension
    text = f"""{gc("inline_prefix")}{file_name[:-4]}{gc("inline_separator")}{page} OR {gc("inline_prefix")}{file_name}{gc("inline_separator")}{page}"""
    browser = aqt.dialogs.open("Browser", mw)
    browser.form.searchEdit.lineEdit().setText(text)
    browser.onSearchActivated()


def new_add_window_referencing_this_page(file_name, page):  # unused
    # TODO only useful if added to the right field for the right note type
    # file_name already has .pdf extension
    text = f"""{gc("inline_prefix")}{file_name[:-4]}{gc("inline_separator")}{page}"""
    addcards = aqt.dialogs.open("AddCards", mw=aqt.mw)
    addcards.editor.note["Front"] = text
    addcards.editor.loadNoteKeepingFocus()



class MyAnkiWebPage(AnkiWebPage):
     def acceptNavigationRequest(self, url, navType, isMainFrame):
        return super(AnkiWebPage, self).acceptNavigationRequest(url, navType, isMainFrame)


class WebViewForPdfjs(QWebEngineView):
    pycmd_page_in_browser = "pdfjs_page_in_browser____"
    pycmd_page_to_clip = "pdfjs_page_to_clip____"

    def __init__(self, parent=mw):
        QWebEngineView.__init__(self, parent=parent)
        self.parent = parent
        self._page = MyAnkiWebPage(self._onBridgeCmd)
        self._page.setBackgroundColor(QColor("#2f2f31") if anki_point_version <= 54 else theme_manager.qcolor(colors.CANVAS))
        self.new_cb_text = ""
        self.setPage(self._page)

    def _onBridgeCmd(self, cmd: str):
        print(f'in bridge_cmd: cmd is {cmd}')
        ## in AnkiWebView._onBridgeCmd:
        # handled, result = webview_did_receive_js_message(
        #     (False, None), cmd, self._bridge_context
        # )
        # if handled:
        #     return result
        # else:
        #     return self.onBridgeCmd(cmd)
        if cmd.startswith(self.pycmd_page_in_browser):
            page = cmd[len(self.pycmd_page_in_browser):]
            search_in_browser(self.parent.fname, page)
        elif cmd.startswith(self.pycmd_page_to_clip):  # run after afterCopyWithReference
            page = cmd[len(self.pycmd_page_to_clip):]
            self.second_afterCopyWithReference(page)
        else:
            print("unhandled bridge cmd:", cmd)    

    def contextMenuEvent(self, evt: QContextMenuEvent) -> None:
        m = QMenu(self)
        a_copy = m.addAction("copy")
        qconnect(a_copy.triggered, self.onCopy)
        a_refcopy = m.addAction("copy, add reference")
        qconnect(a_refcopy.triggered, self.onCopyWithReference)
        a_reference = m.addAction("show notes referencing this page in browser")
        qconnect(a_reference.triggered, self.show_notes_referencing_page)
        m.popup(QCursor.pos())

    def onCopy(self) -> None:
        self.triggerPageAction(QWebEnginePage.WebAction.Copy)

    def onCopyWithReference(self):
        self.onCopy()
        t = QTimer(mw)
        t.timeout.connect(self.afterCopyWithReference)  # type: ignore
        t.setSingleShot(True)
        t.start(100)   

    def afterCopyWithReference(self):
        cb = mw.app.clipboard().mimeData()
        if not cb.hasText():
            tooltip("clipboard has not text. Aborting ...")
            return
        self.new_cb_text = cb.text()
        js = """
var cur_pdf_page = PDFViewerApplication.pdfViewer.currentPageNumber;
pycmd(`%s${cur_pdf_page}`);
""" % self.pycmd_page_to_clip
        self.page().runJavaScript(js)

    def second_afterCopyWithReference(self, page):
        new_clip = f"""{self.new_cb_text}\n\n{gc("inline_prefix")}{self.parent.fname[:-4]}{gc("inline_separator")}{page}"""
        mw.app.clipboard().setText(new_clip)
        self.new_cb_text = ""

    def show_notes_referencing_page(self):
        js = """
var cur_pdf_page = PDFViewerApplication.pdfViewer.currentPageNumber;
pycmd(`%s${cur_pdf_page}`);
""" % self.pycmd_page_in_browser
        self.page().runJavaScript(js)



class PdfJsViewer(QDialog):
    def __init__(self, parent, url, fname, win_title):
        super(PdfJsViewer, self).__init__(parent)
        if anki_point_version < 45:
            mw.setupDialogGC(self)
        else:
            mw.garbage_collect_on_dialog_finish(self)
        self.parent = parent
        self.url = url
        self.fname = fname
        self.setWindowTitle(win_title)
        self.resize(500, 500)
        restoreGeom(self, "319501851")
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        self.web = WebViewForPdfjs(self)
        self.web.title = "pdfjs"
        mainLayout.addWidget(self.web)
        QMetaObject.connectSlotsByName(self)
        self.web.load(QUrl(self.url))
        self.web.loadFinished.connect(self.load_finished)
        # self.web.setFocus()
        self.exit_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.exit_shortcut.activated.connect(self.reject)

    def reject(self):
        saveGeom(self, "319501851")
        QDialog.reject(self)

    def closeEvent(self, evnt):
        saveGeom(self, "319501851")

    def toggle_to_dark_inverted(self):
        # this code uses the new preference, viewerCssTheme from 2020-11,  https://github.com/mozilla/pdf.js/pull/12625
        # also see https://stackoverflow.com/questions/73390781/properly-switch-to-dark-theme-in-pdf-js-rendered-inside-a-qwebview
        # about applying the theme: https://github.com/mozilla/pdf.js/issues/14059#issuecomment-1002790116
        # viewerCssTheme does not affect the color of the scrollbars and the background color of the pdf file 
        
        # the scrollbar color can be fixed by adding some css to viewer.css, see
        # https://stackoverflow.com/questions/73390781/properly-switch-to-dark-theme-in-pdf-js-rendered-inside-a-qwebview#73426867

        # about the page color: invert them with https://stackoverflow.com/questions/61814564/how-can-i-enable-dark-mode-when-viewing-a-pdf-file-in-firefox
        # js_dark = """(function(){viewer.style = 'filter: grayscale(1) invert(1) sepia(1) contrast(75%)';})()"""
        js_dark = """
javascript:(function(){
viewer.style = 'filter: grayscale(1) invert(1) sepia(1) contrast(75%)';
})()
"""
        self.web.page().runJavaScript(js_dark)

    def load_finished(self, success):
        if success:
            js_dark_theme = """
PDFViewerApplicationOptions.set('viewerCssTheme', 2);
PDFViewerApplication._forceCssTheme();
"""
            # self.web.page().runJavaScript(js_dark_theme)  # modify pdfjs directly to avoid white flicker
            self.web.show()
            if theme_manager.night_mode and gc("apply night mode hacks to invert colors by default"):
                t = QTimer(mw)
                t.timeout.connect(self.toggle_to_dark_inverted)  # type: ignore
                t.setSingleShot(True)
                t.start(gc("night mode adjustment delay in ms", 1000))   

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
        self.setGeometry(0, 28, 650, 450)
        restoreGeom(self, "319501851chromium")
        self.webview = QWebEngineView()
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        mainLayout.addWidget(self.webview)
        url_as_qurl = QUrl(url)
        self.webview.load(url_as_qurl)
        self.exit_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.exit_shortcut.activated.connect(self.reject)

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
        t = QTimer(mw)
        t.timeout.connect(self.go_to_page)  # type: ignore
        t.setSingleShot(True)
        t.start(1000)   
        self.go_to_page()
        if gc("chromium pdf viewer (2.1.50/qt6+ only): invert color hack", None):
            self.invert_page_color()

    def reject(self):
        saveGeom(self, "319501851chromium")
        QDialog.reject(self)

    def closeEvent(self, evnt):
        saveGeom(self, "319501851chromium")

    def invert_page_color(self):
        # see https://superuser.com/a/1527417 by the user Wasif is CC BY-SA 4.0
        # this snippet is widely posted.
        # In 2022-10 this has the same result for me as the short
        #    document.querySelector('embed').style.filter = 'invert()'
        # I got the shortes snippet from
        # https://www.reddit.com/r/edge/comments/h9k5vb/comment/fvb28ze/?utm_source=share&utm_medium=web2x&context=3
        #
        # the problem is that both snippets invert all colors - not just the pdf page as I want
        # but it also turns the dark elements bright - the opposite of what I want.
        #
        # The chrome extension DarkReader has the same shortcoming as the inversion code.
        # So in 2022-10 there's probably no real solution.
        # TODO
        js = """
document.querySelector('embed').style.filter = 'invert()'
"""
        # self.webview.page().runJavaScript(js)


handledfile = None


def parent_to_use(parent):
    if gc("set no parent for pdfjs dialog", False):
        return None
    else:
        return parent


def maybe_move_dialog(d, parent):
    pref = gc("dialog move besides current window")
    if pref == "left":
        move_window(left=d, right=parent, newpos="side-by-side")
    elif pref == "right":
        move_window(left=parent, right=d, newpos="side-by-side")


def open_pdf_in_internal_viewer__with_pdfjs(parent, file, page):
    fmt = f"?file=/_pdfjspath/{file}#page={page}"
    win_title = 'Anki - pdf viewer'
    port = mw.mediaServer.getPort()
    if qtmajor == 6:
        url = f"http://127.0.0.1:{port}/_addons/{addonfoldername}/web/pdfjs/web/viewer.html{fmt}"
    else:
        url = f"http://127.0.0.1:{port}/_addons/{addonfoldername}/web/pdfjs_legacy/web/viewer.html{fmt}"
    d = PdfJsViewer(parent_to_use(parent), url, file, win_title)
    d.show()
    maybe_move_dialog(d, parent)


def open_pdf_in_internal_viewer__with_chromium_pdf(parent, file, page):
    win_title = 'Anki - pdf viewer'
    port = mw.mediaServer.getPort()
    # url = f"{file}#page={page}"  # for pdfs in the media folder
    url = f"http://127.0.0.1:{port}/_pdfjspath/{file}#page={page}"
    # parent=None means the window is closed immediately (in contrast to the pdfjs dialog)
    d = ChromiumPdfViewerWindow(parent, url, win_title)
    d.show()
    maybe_move_dialog(d, parent)


def open_pdf_in_internal_viewer_helper(parent, file, page, not_exist_warning=None):
    global handledfile
    if not_exist_warning:
        showInfo(not_exist_warning)
        return
    handledfile = file
    if anki_point_version <= 49 or qtmajor == 5 or gc("use pdfjs to show pdfs in Anki 2.1.50+ (with pyqt6)", False):
        open_pdf_in_internal_viewer__with_pdfjs(parent, file, page)
    else:
        open_pdf_in_internal_viewer__with_chromium_pdf(parent, file, page)
mw.pdf_folder_path = gc("pdf_folder_paths")
mw.open_pdf_in_internal_viewer_helper = open_pdf_in_internal_viewer_helper


def basic_check_filefield(file_with_or_without, page, showinfos):
    if file_with_or_without.startswith("file:/"):
        vmsg = ("illegal values in field '%s'. See description of the add-on "
                "'anki pdf viewer (pdfjs)' on Ankiweb. Aborting..." % 
                gc("field_for_filename", "")
                )
        if showinfos:
            showInfo(vmsg)
        return None, None, None

    # ugly workaround to guess file extension 
    # - I use this approach because this means I can reuse code from 879473266 without changing it
    # - I use this approach because this means no modification for users of their old hyperlink
    #   code in their card templates is needed.
    re_merged = f"""{gc("inline_prefix")}{file_with_or_without}{gc("inline_separator")}{page}"""
    file_abs, page = check_string_for_existing_file(re_merged)

    if not file_abs or not os.path.isfile(file_abs):
        nemsg = ("The file '%s' does not exist in the folder '%s'. Maybe "
                 "the file is missing, maybe there's a typo or maybe "
                 "there's too much else in the field '%s'. Aborting ..."
                 "\nAlso see the description of the add-on "
                 "''anki pdf viewer (pdfjs)' on ankiweb." % (
                  file_with_or_without, gc("pdf_folder_paths"), gc("field_for_filename"))
                 )
        if showinfos:
            showInfo(nemsg)
        return None, None, nemsg

    if file_abs:
        just_filename = os.path.basename(file_abs)  # convert abs back to relative
        return just_filename, page, None
    return None, None, None


def myLinkHandler(self, parent, url, _old):
    if url.startswith("pdfjs319501851"):
        file_with_or_without_encoded, page = url.replace("pdfjs319501851", "").split("319501851")
        file_with_or_without_decoded = base64.b64decode(file_with_or_without_encoded).decode('utf-8')
        file_rel_path_if_exists, page, does_not_exist_show_warning = basic_check_filefield(file_with_or_without_decoded, page, True)
        if file_rel_path_if_exists:
            open_pdf_in_internal_viewer_helper(parent, file_rel_path_if_exists, page)
    else:    
        return _old(self, url)


def myLinkHandler_reviewer(self, url, _old):
    myLinkHandler(self, mw, url, _old)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler_reviewer, "around")


def myLinkHandler_previewer(self, url, _old):
    myLinkHandler(self, self, url, _old)
Previewer._on_bridge_cmd = wrap(Previewer._on_bridge_cmd, myLinkHandler_previewer, "around")


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


def my_helper(editor, menu):
    filefld = [f["ord"] for f in editor.note.model()['flds'] if f['name'] == gc("field_for_filename")]
    if not filefld:
        return
    file_with_or_without = stripHTML(editor.note.fields[filefld[0]])
    pagefld = [f["ord"] for f in editor.note.model()['flds'] if f['name'] == gc("field_for_page")]
    page = ""
    if pagefld:
        page = stripHTML(editor.note.fields[pagefld[0]])
    file_rel_path_if_exists, page, does_not_exist_show_warning = basic_check_filefield(file_with_or_without, page, False)
    if file_rel_path_if_exists:
        a = menu.addAction("open pdf")
        a.triggered.connect(lambda _, pw=editor.parentWindow, f=file_rel_path_if_exists, pa=page, m=does_not_exist_show_warning: open_pdf_in_internal_viewer_helper(pw,f,pa, m))


def add_to_context(view, menu):
    e = view.editor
    field = e.currentField
    if field:
        e.saveNow(lambda ed=e, m=menu: my_helper(ed, m))
    else:
        my_helper(e, menu)
addHook("EditorWebView.contextMenuEvent", add_to_context)  # noqa
