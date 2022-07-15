from pprint import pprint as pp  # noqa

from anki.hooks import wrap
from aqt.clayout import CardLayout
from aqt.utils import showInfo
from aqt.qt import *

from .anki_version_detection import anki_point_version
from .config import gc

    if qtmajor == 5:
        from .forms5 import addtofield28 as addtofield  # noqa
    else:
        from .forms6 import addtofield28 as addtofield  # noqa


def my_setup_buttons(self):
    on_ext_docs_but = QPushButton("PDF open from fields code")
    on_ext_docs_but.setAutoDefault(False)
    self.buttons.insertWidget(3, on_ext_docs_but)
    on_ext_docs_but.clicked.connect(self.on_ext_docs_link)
    tm = ("This button belongs to the add-on 'anki pdf viewer'."
          "For more info go to https://ankiweb.net/shared/info/319501851")
    on_ext_docs_but.setToolTip(tm)
CardLayout.setupButtons = wrap(CardLayout.setupButtons, my_setup_buttons)  # noqa


def on_ext_docs_link(self):
    filefield = gc("field_for_filename", "external_source")
    pagefield = gc("field_for_page", "external_page")
    fieldnames = [f['name'] for f in self.model['flds']]
    if filefield not in fieldnames or pagefield not in fieldnames:
        msg = ("Your setup for the Add-on 'anki pdf viewer' "
               "is not valid.\n\n"
               "Your notetype doesn't contain fields with the names %s and %s "
               "which you set in the config of this add-on. Either use one of the note "
               "types bundled with this add-on or add fields with these names to this note type.\n\n"
               "If you don't know what I mean by 'add fields to your note type' watch "
               "this video https://www.youtube.com/watch?v=JTKqd4nqsK0&feature=youtu.be&t=22" % (
                   filefield, pagefield
               ))
        showInfo(msg)
        return
    diag = QDialog(self)
    form = addtofield.Ui_Dialog()
    form.setupUi(diag)
    form.linktext.setText("View external file: {{text:%s}}" % filefield)
    form.font.setCurrentFont(QFont("Arial"))
    form.size.setValue(20)
    diag.show()
    if not diag.exec():
        return
    obj = self.tform.edit_area
    t = obj.toPlainText()
    t += ("""\n<a href='javascript:pycmd("pdfjs319501851"""
          """{{text:%s}}319501851{{text:%s}}");'"""
          """>%s</a>""" % (filefield, pagefield, form.linktext.text()))
    obj.setPlainText(t)
CardLayout.on_ext_docs_link = on_ext_docs_link  # noqa
