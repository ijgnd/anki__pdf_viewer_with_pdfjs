# this file is actually different from the file of the same name from 879473266/Open linked pdf, docx, epub, ...

# the code here is basically the same I added to
# with the commit a0e1021 2022-07-13 19:28:20 +0200 ijgnd show pdfs with bundled/built-in viewer using 319501851/pdf viewer

import os

from aqt import mw

def open_external(file, page):
    if mw.pdf_folder_path in file and file.endswith("pdf"):
        filename = os.path.basename(file)
        mw.open_pdf_in_internal_viewer_helper(filename, page)
