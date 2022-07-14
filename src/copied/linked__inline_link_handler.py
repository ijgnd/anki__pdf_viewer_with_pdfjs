import aqt
from aqt import mw
from aqt.utils import tooltip

from .config import gc, pycmd_string
from .helpers import check_string_for_existing_file
from .open_in_external import open_external


def process_urlcmd(url):
    if url.startswith(pycmd_string):
        file, page = check_string_for_existing_file(url.replace(pycmd_string, ""))
        # print(f"file_add_to_context: {file}, {page}")
        if file:
            open_external(file, page)
        else:
            tooltip("maybe the file doesn't exist. Maybe there's a bug in the add-on 'Open linked ...'")
        return True
    return False
