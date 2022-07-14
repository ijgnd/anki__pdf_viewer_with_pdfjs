import os

import aqt

from .config import addon_path, gc


addons_folder = aqt.mw.addonManager.addonsFolder()
open_linked_file_externally_folder = os.path.join(addons_folder, "879473266")
if os.path.isdir(open_linked_file_externally_folder):
    addon_externally_installed = True
else:
    addon_externally_installed = False

if addon_externally_installed:
    warning = """
There's a conflict between the add-ons "pdf viewer" (https://ankiweb.net/shared/info/319501851)
and "Open linked pdf, docx, epub, audio/video, etc. in external Program"
(https://ankiweb.net/shared/info/879473266).

This conflict arises because in the add-on "pdf viewer" in the user config you have set
"inline modification enabled" to "true". To avoid this problem either disable/uninstall
one of the add-ons or set "inline modification enabled" to "false".

If you do nothing you will run into strange errors.
"""
    msg_fmt = warning.replace("\n\n","qqq").replace("\n", " ").replace("qqq","\n\n")
    aqt.utils.showInfo(msg_fmt[1:-1], title="Addon Conflict")  # [1:-1] strip leading/ending space


from . import pdf
from . import card_layout
from . import settings

if gc("inline modification enabled"):
    from .copied import editor_insert_reference
    from .copied import linked__inline_editor
    from .copied import linked__inline_view
