import json
import os

from aqt.qt import (
    QKeySequence,
)
from aqt.utils import (
    tooltip,
)
from aqt.gui_hooks import (
    editor_did_init_buttons
)

from .config import (
    addon_path,
    gc,
)


from .fuzzy_panel import FilterDialog
from .helpers import (
    get_all_relative,
)


def insert_file_name_formatted(editor):
    _, filenames = get_all_relative(relative_only=True)
    d = FilterDialog(parent=editor.parentWindow, values=filenames)
    if d.exec():
        file = d.selkey
    else:
        return
    file_wo, _ = os.path.splitext(file)
    ins = file_wo if gc("insert filenames without extension") else file
    fmted = gc("inline_prefix", "___") + ins + gc("inline_separator", "____")
    editor.web.eval("setFormat('inserthtml', %s);" % json.dumps(fmted))
    if " " in file:
        tooltip("There's a space in file name inserted. This breaks <br>some functions of the add-on 'open linked pdfs'.")


def keystr(k):
    key = QKeySequence(k)
    return key.toString(QKeySequence.SequenceFormat.NativeText)


def addEditorButton(buttons, editor):
    if not gc("inline_prefix"):
        return buttons
    scut = gc("shortcut_insert_filename", "")
    b = editor.addButton(
        icon=os.path.join(addon_path, "icons", "folder-plus_mod.svg"),
        cmd="linked_pdf_inserter_button",
        func=insert_file_name_formatted,
        tip=f"Insert file name from default folder (pdf link add-on) ({keystr(scut)})",
        keys=scut
        )
    buttons.append(b)
    return buttons
editor_did_init_buttons.append(addEditorButton)
