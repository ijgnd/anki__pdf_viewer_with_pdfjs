import io
import json
import os
import re
from pprint import pprint as pp  # noqa

from anki.hooks import addHook
from anki.utils import (
    isLin,
    isMac,
    isWin,
    pointVersion,
)
from aqt import mw
from aqt.qt import *
from aqt.utils import (
    showInfo,
)
from .config import gc

if qtmajor == 5:
    from .forms5 import first_run_import  # noqa
else:
    from .forms6 import first_run_import  # noqa


def MaybeSetPath():
    config = mw.addonManager.getConfig(__name__.split(".")[0])
    updateconf = False
    if "pdf_folder_paths" not in config:
        updateconf = True
    else:
        if not config["pdf_folder_paths"]:
            updateconf = True
        else:
            if not os.path.exists(config["pdf_folder_paths"]):
                updateconf = True
    if updateconf:
        if isMac:
            # https://stackoverflow.com/a/57002816
            # Finder shows localized names for standard folders in your language but uses standard
            # names on system level.
            FOLDER = os.path.join(os.path.expanduser("~"), "Documents", "Ankifiles")
        elif isWin:
            import ctypes.wintypes
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
            FOLDER = os.path.join(buf.value, "Ankifiles")
        else:
            docs_in_e = os.path.join(os.path.expanduser("~"), "Documents")
            if os.path.isdir(docs_in_e):
                FOLDER = os.path.join(docs_in_e, "Ankifiles")
            else:
                FOLDER = os.path.join(os.path.expanduser("~"), "Ankifiles")
        config["pdf_folder_paths"] = FOLDER
        mw.addonManager.writeConfig(__name__, config)
addHook("profileLoaded", MaybeSetPath)


def exists_model(modmodels, thismodel):
    for m in mw.col.models.all():
        if thismodel['name'] in m["name"] or thismodel['id'] == m["name"]:
            return True
    return


class SelectNoteImport(QDialog):
    def __init__(self, parent=None, entries=[]):
        self.parent = parent
        QDialog.__init__(self, parent, Qt.WindowType.Window)
        self.dialog = first_run_import.Ui_Dialog()
        self.dialog.setupUi(self)
        ltext = ("This window is shown by the add-on 'anki pdf viewer (pdfjs)'.\n\nThis "
                 "message is only shown one time after installing it.\n"
                 "To see this message again enable it in the add-on settings of this add-on "
                 "from the add-on manager.\n\n"
                 "Instead of importing these easy-to-use pre-configured note types you can also "
                 "adjust your existing note types.\nFor details see the description at "
                 "https://ankiweb.net/shared/info/319501851.\n\n"
                 "If you decide to import some of the note types below you can delete them later\n"
                 "from the 'Manage Note Types' dialog if you don't like or need them anymore.\n\n"
                 "Select which note types that are preconfigured for this add-on should be "
                 "available to you in the future:\n"
                 )
        self.dialog.ql_top.setText(ltext)
        self.dialog.cb_basic.setText("Basic (with pdf references)")
        self.dialog.cb_cloze.setText("Cloze (with pdf references)")
        self.dialog.cb_opt_reverse.setText("Basic (optional reversed card, with pdf references)")
        self.dialog.cb_reverse.setText("Basic (and reversed card, with pdf references)")
        self.dialog.cb_typein.setText("Basic (type in the answer, with pdf references)")
        self.dialog.buttonBox.accepted.disconnect(self.accept)
        self.dialog.buttonBox.accepted.connect(self.onAccept)

    def onAccept(self):
        mta = []
        if self.dialog.cb_basic.isChecked():
            mta.append("adjBasic")
        if self.dialog.cb_cloze.isChecked():
            mta.append("adjCloze")
        if self.dialog.cb_opt_reverse.isChecked():
            mta.append("adjBasicOptReverse")
        if self.dialog.cb_reverse.isChecked():
            mta.append("adjBasicReverse")
        if self.dialog.cb_typein.isChecked():
            mta.append("adjBasicTypeIn")
        if mta:
            addon_path = os.path.dirname(__file__)
            jsonpath = os.path.join(addon_path, "models.json")
            with io.open(jsonpath, encoding="utf-8") as f:
                mij = f.read()
            modmodels = json.loads(mij)
            skiplist = []
            for e in mta:
                thismodel = modmodels[e]
                if exists_model(modmodels, thismodel):
                    skiplist.append(thismodel['name'])
                else:
                    mw.col.models.add(thismodel)
            if skiplist:
                skipmsg = ("The note types\n- %s\nalready seem to exist. Skipping these..." %
                           ",\n- ".join(skiplist))
                showInfo(skipmsg)
        self.accept()


def MaybeAddModels():
    config = mw.addonManager.getConfig(__name__.split(".")[0])
    if config.get("show_first_run_message", True) and pointVersion() < 45:
        config["show_first_run_message"] = False
        mw.addonManager.writeConfig(__name__.split(".")[0], config)
        d = SelectNoteImport()
        d.exec()
addHook("profileLoaded", MaybeAddModels)  # noqa
