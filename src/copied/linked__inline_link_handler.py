import base64

import aqt
from aqt import mw
from aqt.utils import tooltip

from .config import gc, pycmd_string, pycmd_string_editor
from .helpers import check_string_for_existing_file
from .open_in_external import open_external


def process_urlcmd(parent, url):
    if url.startswith(pycmd_string):
        encoded_file_and_page = url.replace(pycmd_string, "")
        decoded = base64.b64decode(encoded_file_and_page).decode('utf-8')
        file, page = check_string_for_existing_file(decoded)
        # print(f"file_add_to_context: {file}, {page}")
        if file:
            open_external(parent, file, page)
        else:
            tooltip("maybe the file doesn't exist. Maybe there's a bug in the add-on 'pdf viewer ...'")
        return True
    if url.startswith(pycmd_string_editor):
        file, page = check_string_for_existing_file(url.replace(pycmd_string_editor, ""))
        # print(f"file_add_to_context: {file}, {page}")
        if file:
            open_external(parent, file, page)
        else:
            tooltip("maybe the file doesn't exist. Maybe there's a bug in the add-on 'pdf viewer ...'")
        return True
    return False
