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
    if editor.currentField is None:
        tooltip("No field selected. Aborting ...")
        return
    inline_allowed = True
    for idx, fname in enumerate(editor.note.keys()):
        if idx == editor.currentField:
            if fname == gc("field_for_filename"):
                inline_allowed = False
    _, filenames = get_all_relative(relative_only=True)
    dialog = FilterDialog(parent=editor.parentWindow, 
                          values=filenames,
                          inline_allowed=inline_allowed,
                          windowtitle="select filename to insert"
                        )
    if dialog.exec():
        file = dialog.selkey
    else:
        return
    file_wo, _ = os.path.splitext(file)
    ins = file_wo if gc("insert filenames without extension") else file
    if dialog.surrounded:
        ins = gc("inline_prefix", "___") + ins + gc("inline_separator", "____")
    editor.web.eval("setFormat('inserthtml', %s);" % json.dumps(ins))


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
