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

from anki.hooks import addHook, wrap
from anki.utils import (
    stripHTML,
)
from .anki_version_detection import anki_point_version
from .config import gc

from aqt import mw
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
import aqt.mediasrv as mediasrv

from .copied.helpers import check_string_for_existing_file


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
        self.parent = parent
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

    def toggle_to_dark_inverted(self):
        # TODO
        # look into "new preference, viewerCssTheme" from 2020-11,  https://github.com/mozilla/pdf.js/pull/12625


        # basic solution from https://stackoverflow.com/questions/61814564/how-can-i-enable-dark-mode-when-viewing-a-pdf-file-in-firefox
        # js_dark = """(function(){viewer.style = 'filter: grayscale(1) invert(1) sepia(1) contrast(75%)';})()"""
        # an extended bookmarklet from 2020
        js_dark = """
javascript:(function(){
viewer.style = 'filter: grayscale(1) invert(1) sepia(1) contrast(75%)';
document.getRootNode().body.style.setProperty('--body-bg-color', 'Black');
document.getElementById("pageNumber").style.setProperty('background-color', '#2c2c2c');
document.getElementById("pageNumber").style.setProperty('color', '#afb0a4');
document.getElementById("numPages").style.setProperty('background-color', '#2c2c2c');
document.getElementById("numPages").style.setProperty('color', '#afb0a4');
document.getElementById("scaleSelectContainer").style.setProperty('color', '#afb0a4');
document.getElementById("scaleSelectContainer").style.setProperty('color', '#afb0a4');
document.getElementById("toolbarViewer").style.setProperty('background-color', '#2c2c2c');
document.getElementById("scaleSelect").style.setProperty('background-color', '#2c2c2c');
document.getElementById("scaleSelect").style.setProperty('color', '#afb0a4');
})()
        """


        '''
        # new answer from 2022 from https://stackoverflow.com/a/71777470 doesn't help
        js_dark = """
(
    function() {
        if (viewer.classList.contains("dm")) viewer.style = "";
        else viewer.style = "filter: grayscale(1) invert(1) sepia(1) contrast(75%)'";
        viewer.classList.toggle("dm");
    }
)()
"""
'''
        # suggested at https://github.com/mozilla/pdf.js/issues/2071#issuecomment-830446509
        # js_dark = """(function(){viewer.style.filter = 'invert(64%) contrast(228%) brightness(80%) hue-rotate(180deg)';})()"""
        self.web.page().runJavaScript(js_dark)

    def load_finished(self, success):
        if success:
            self.web.show()
            if theme_manager.night_mode and gc("apply night mode hacks to invert colors by default"):
                t = QTimer(self.parent)
                t.timeout.connect(self.toggle_to_dark_inverted)  # type: ignore
                t.setSingleShot(True)
                t.start(1000)   

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
        #self.invert_colors()

    def invert_colors(self):
        # see https://superuser.com/a/1527417
        # the original code by the user Wasif is CC BY-SA 4.0
        # this code is modified.
        # doesn't help because the pdfium elements like the sidebar or background
        # are still grey.
        js = """
const overlay = document.createElement("div");
const css = `
    position: fixed;
    pointer-events: none;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: white;
    mix-blend-mode: difference;
    z-index: 1;
`
overlay.setAttribute("style", css);
document.body.appendChild(overlay);

// https://stackoverflow.com/a/21581690 - load jquery
// Immediately-invoked function expression
(function() {
  // Load the script
  const script = document.createElement("script");
  script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js';
  script.type = 'text/javascript';
  script.addEventListener('load', () => {
    console.log(`jQuery ${$.fn.jquery} has been loaded successfully!`);
    // use jQuery below
  });
  document.head.appendChild(script);
})();


// manually replace colors with jquery - https://stackoverflow.com/a/30724171
// this breaks the css hack
function colorReplace(findHexColor, replaceWith) {
  // Convert rgb color strings to hex
  // REF: https://stackoverflow.com/a/3627747/1938889
  function rgb2hex(rgb) {
    if (/^#[0-9A-F]{6}$/i.test(rgb)) return rgb;
    rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    function hex(x) {
      return ("0" + parseInt(x).toString(16)).slice(-2);
    }
    return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
  }

  // Select and run a map function on every tag
  $('*').map(function(i, el) {
    // Get the computed styles of each tag
    var styles = window.getComputedStyle(el);

    // Go through each computed style and search for "color"
    Object.keys(styles).reduce(function(acc, k) {
      var name = styles[k];
      var value = styles.getPropertyValue(name);
      if (value !== null && name.indexOf("color") >= 0) {
        // Convert the rgb color to hex and compare with the target color
        if (value.indexOf("rgb(") >= 0 && rgb2hex(value) === findHexColor) {
          // Replace the color on this found color attribute
          $(el).css(name, replaceWith);
        }
      }
    });
  });
}

// Call like this for each color attribute you want to replace
//colorReplace("#ada9a6", "#21222c");
"""
        self.webview.page().runJavaScript(js)


handledfile = None


def open_pdf_in_internal_viewer__with_pdfjs(parent, file, page):
    fmt = f"?file=/_pdfjspath/{file}#page={page}"
    win_title = 'Anki - pdf viewer'
    port = mw.mediaServer.getPort()
    if gc("pdf_js_version_used") == "mid_2021":
        url = f"http://127.0.0.1:{port}/_addons/{addonfoldername}/web/pdfjs_mid_2021/web/viewer.html{fmt}"
    else:
        # the regular version from https://github.com/mozilla/pdf.js/releases/download/v2.14.305/pdfjs-2.14.305-dist.zip
        # does not work with anki 2.1.49 in 2022-07-13
        url = f"http://127.0.0.1:{port}/_addons/{addonfoldername}/web/pdfjs_2022-05-14__v2.14.305_legacy/web/viewer.html{fmt}"
    d = PdfJsViewer(parent, url, win_title)
    d.show()


def open_pdf_in_internal_viewer__with_chromium_pdf(parent, file, page):
    win_title = 'Anki - pdf viewer'
    port = mw.mediaServer.getPort()
    # url = f"{file}#page={page}"  # for pdfs in the media folder
    url = f"http://127.0.0.1:{port}/_pdfjspath/{file}#page={page}"
    d = ChromiumPdfViewerWindow(parent, url, win_title)
    d.show()


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
