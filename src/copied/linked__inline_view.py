import re

from anki.hooks import wrap
from aqt import gui_hooks
from aqt import mw
from aqt.browser import Browser
from aqt.editor import Editor
from aqt.previewer import Previewer
from aqt.reviewer import Reviewer
from aqt.utils import tooltip


from .config import gc, pycmd_string
from .helpers import check_string_for_existing_file
from .linked__inline_link_handler import process_urlcmd
from .open_in_external import open_external



def myLinkHandler(self, url, _old):
    if process_urlcmd(url):
        return
    else:
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")
Previewer._on_bridge_cmd = wrap(Previewer._on_bridge_cmd, myLinkHandler, "around")
Editor.onBridgeCmd = wrap(Editor.onBridgeCmd, myLinkHandler, "around")


def contexthelper(menu, selectedtext):
    if not gc("inline_prefix"):
        return
    if not gc("inline_prefix") in selectedtext:
        return
    file, page = check_string_for_existing_file(selectedtext)
    # print(f"file_add_to_context: {file}, {page}")
    if file:
        a = menu.addAction("Try to open externally")
        a.triggered.connect(lambda _, f=file, p=page: open_external(f, p))


def EditorContextMenu(view, menu):
    selectedtext = view.editor.web.selectedText()
    contexthelper(menu, selectedtext)


def ReviewerContextMenu(view, menu):
    if mw.state != "review":
        return
    selectedtext = view.page().selectedText()
    contexthelper(menu, selectedtext)


def actually_transform(txt):
    pattern = r"(%s.*?%s\d{0,4})" % (gc("inline_prefix", "___"), gc("inline_separator", "____"))
    repl = """<a href='javascript:pycmd("%s\\1");'>\\1</a>""" % pycmd_string
    txt = re.sub(pattern, repl, txt)
    return txt


def transform(text, card, kind):
    if kind in [
        "previewQuestion", 
        "previewAnswer", 
        "reviewQuestion", 
        "reviewAnswer",
        "clayoutQuestion",
        "clayoutAnswer",
    ]:
        return actually_transform(text)
    else:
        return text


alreadyloaded = False
def on_profile_loaded():
    global alreadyloaded
    if alreadyloaded:
        return
    alreadyloaded = True
    """user config only available when profile is loaded"""
    iprfx = gc("inline_prefix", None)
    if iprfx == None or not isinstance(iprfx, str):
        return
    if gc('context menu entries in reviewer', True):
        gui_hooks.webview_will_show_context_menu.append(ReviewerContextMenu)
    if gc('context menu entries in editor', True):
        gui_hooks.editor_will_show_context_menu.append(EditorContextMenu)
    if gc("make inline prefixed clickable", True):
        gui_hooks.card_will_show.append(transform)
gui_hooks.profile_did_open.append(on_profile_loaded)
