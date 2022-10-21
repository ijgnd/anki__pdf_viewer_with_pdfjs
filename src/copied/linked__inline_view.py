import base64
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



def myLinkHandler_reviewer(self, url, _old):
    if process_urlcmd(mw, url):
        return
    else:
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler_reviewer, "around")

def myLinkHandler_previewer(self, url, _old):
    if process_urlcmd(self, url):
        return
    else:
        return _old(self, url)
Previewer._on_bridge_cmd = wrap(Previewer._on_bridge_cmd, myLinkHandler_previewer, "around")


def myLinkHandler_editor(self, url, _old):
    if process_urlcmd(self.parentWindow, url):
        return
    else:
        return _old(self, url)
Editor.onBridgeCmd = wrap(Editor.onBridgeCmd, myLinkHandler_editor, "around")


def contexthelper(menu, parent, selectedtext):
    if not gc("inline_prefix"):
        return
    if not gc("inline_prefix") in selectedtext:
        return
    file, page = check_string_for_existing_file(selectedtext)
    # print(f"file_add_to_context: {file}, {page}")
    if file:
        a = menu.addAction("Try to open externally")
        a.triggered.connect(lambda _, p=parent, f=file, pg=page: open_external(p, f, pg))


def EditorContextMenu(view, menu):
    selectedtext = view.editor.web.selectedText()
    contexthelper(menu, view.editor.parentWindow, selectedtext)


def ReviewerContextMenu(view, menu):
    if mw.state != "review":
        return
    selectedtext = view.page().selectedText()
    contexthelper(menu, mw, selectedtext)


def my_replace(match):
    match = match.group()
    encoded = base64.urlsafe_b64encode(match.encode('utf-8')).decode("utf-8")
    return f"""<a class="pdfjsaddon_inline" href='javascript:pycmd("{pycmd_string}{encoded}");'>{match}</a>"""


def actually_transform(txt):
    pattern = r"(%s.*?%s\d{0,4})" % (gc("inline_prefix", "___"), gc("inline_separator", "____"))
    txt = re.sub(pattern, my_replace, txt)
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
    if gc('context menu entries in editor', True):  # already in pdf.py
        gui_hooks.editor_will_show_context_menu.append(EditorContextMenu)
    if gc("make inline prefixed clickable", True):
        gui_hooks.card_will_show.append(transform)
gui_hooks.profile_did_open.append(on_profile_loaded)
