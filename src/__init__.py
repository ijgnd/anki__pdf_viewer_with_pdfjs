# for licensing info see the bottom of config.md

import os
import shutil

import aqt

from .config import addon_path, gc, wc
from .info_dialog_scrollable import InfoDialog

addons_folder = aqt.mw.addonManager.addonsFolder()
open_linked_file_externally_folder = os.path.join(addons_folder, "879473266")
if os.path.isdir(open_linked_file_externally_folder):
    addon_externally_installed = True
else:
    addon_externally_installed = False

if addon_externally_installed:
    messages_shown = gc("update_messages_shown", [])
    if not "conflict_warning_879473266" in messages_shown:
        warning = """
There's a conflict between the add-ons "pdf viewer" (https://ankiweb.net/shared/info/319501851)
and "Open linked pdf, docx, epub, audio/video, etc. in external Program"
(https://ankiweb.net/shared/info/879473266).

This conflict arises because in the add-on "pdf viewer" in the user config you have set
"inline modification enabled" to "true". To avoid this problem either disable/uninstall
one of the add-ons or set "inline modification enabled" to "false".

If you do nothing you will run into strange errors.

This message is just shown once.
"""
        msg_fmt = warning.replace("\n\n","qqq").replace("\n", " ").replace("qqq","\n\n")
        aqt.utils.showInfo(msg_fmt[1:-1], title="Addon Conflict")  # [1:-1] strip leading/ending space
        wc("update_messages_shown", messages_shown + ["conflict_warning_879473266"])


from . import pdf
from . import card_layout
from . import settings

if gc("inline modification enabled"):
    from .copied import editor_insert_reference
    from .copied import linked__inline_editor
    from .copied import linked__inline_view


def write_js_on_profile_loaded():
    media_dir = aqt.mw.col.media.dir()
    js_src_abs = os.path.join(addon_path, "_js_base64_minified_for_pdf_viewer_addon.js")
    js_media_abs = os.path.join(media_dir, "_js_base64_minified_for_pdf_viewer_addon.js")
    if not os.path.isfile(js_media_abs):
        shutil.copy(js_src_abs, js_media_abs)
aqt.gui_hooks.profile_did_open.append(write_js_on_profile_loaded)



def maybe_warn_on_profile_loaded():
    messages_shown = gc("update_messages_shown", [])
    if not "2022-07-15" in messages_shown:
        msg = """
<b>This is a one-time message from the add-on "pdf viewer" that you just
installed or updated.
<br><br>
If you just installed the add-on: Ignore this message.
<br><br>
If you just updated the add-on: You must manually modify all
card templates and change the code that puts the clickable hyperlink
for opening the pdfs in your cards.</b>
<br><br>
This is cumbersome and might take you some minutes.
<br><br>
But this change was necessary because the old code I used in old versions
of this add-on just worked with my narrow use case which consists of file
names with basically just english characters. This approach fails e.g. with
the grave accent used in many western European languages or with other
non-western characters.
<br><br>
Proceed like this: Delete the old code from your card templates and then insert
the new improved code by clicking the button "PDF open from fields code" in the
"Card types for ..." window.
<br><br>
With old code that needs to be removed I refer to a line of code that starts with
<div style="margin-left: 40px;"><code>&lt;a href='javascript:pycmd("pdfjs319501851</code></div>
Remove the code until you get to the first
<div style="margin-left: 40px;"><code>&lt;/a&gt;<code></div>
Between there's code depending on your settings. If you always used the default
settings the code to remove looks like this (ignore the linebreaks in this narrow window):
<div style="margin-left: 40px;"><code>
&lt;a href='javascript:pycmd("pdfjs319501851{{text:external_source}}319501851{{text:external_page}}");'>View external file: {{text:external_source}}/&lt;a&gt;
<code></div>
<br>
If you don't know what I'm talking about: Go to the <a href="https://ankiweb.net/shared/info/319501851">ankiweb page of this add-on</a>.
There I link screencasts that describe how you setup the add-on and on this page in the section
"# further info about the setup" I have links to youtube guides and the relevant
part of the manual.
<br>
These instructions can also be found on the <a href="https://ankiweb.net/shared/info/319501851">ankiweb page of this add-on</a>
in the section "# Updating card templates to the add-on version from 2022-07 or later".
"""    
        #msg_fmt = msg.replace("\n\n","qqq").replace("\n    ", "q1q").replace("\n", " ").replace("qqq","\n\n").replace("q1q", "\n    ")[1:-1]
        dialog = InfoDialog(aqt.mw, "Anki Add-on pdf viewer warning", msg)
        dialog.exec()
        wc("update_messages_shown", messages_shown + ["2022-07-15"])

aqt.gui_hooks.profile_did_open.append(maybe_warn_on_profile_loaded)
