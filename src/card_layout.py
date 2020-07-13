from pprint import pprint as pp

from anki.hooks import wrap
from aqt.clayout import CardLayout
from aqt.utils import showInfo
from aqt.qt import *
from aqt import mw

from .forms import addtofield


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    return fail


def mySetupButtons(self):
    onExtDocsLink = QPushButton("Ext-Docs-Link")
    onExtDocsLink.setAutoDefault(False)
    self.buttons.insertWidget(3, onExtDocsLink)
    onExtDocsLink.clicked.connect(self.onExtDocsLink)
    tm = ("This button belongs to the add-on 'anki pdf viewer (pdfjs)'."
          "For more info go to https://ankiweb.net/shared/info/319501851")
    onExtDocsLink.setToolTip(tm)
CardLayout.setupButtons = wrap(CardLayout.setupButtons, mySetupButtons)


def onExtDocsLink(self):
    filefield =  gc("field_for_filename","external_source")
    pagefield = gc("field_for_page","external_page")
    fieldnames = [f['name'] for f in self.model['flds']]
    if filefield not in fieldnames or pagefield not in fieldnames:
        msg = ("Your setup for the Add-on 'anki pdf viewer (pdfjs)' "
               "is not valid.\n\n"
               "Your notetype doesn't contain fields with the names %s and %s"
               "which you set in the config of this add-on. Either use one of the note"
               "types bundled with this add-on or add fields with these names to this note type.\n\n"
               "If you don't know what I mean by 'add fields to your note type' watch"
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
    if form.radioQ.isChecked():
        obj = self.tform.front
    else:
        obj = self.tform.back
    t = obj.toPlainText()
    t += ("""<a href='javascript:pycmd("pdfjs319501851"""
          """{{text:%s}}319501851{{text:%s}}");'"""
          """>%s</a>""" % (filefield, pagefield, form.linktext.text()))
    obj.setPlainText(t)
    self.saveCard()
CardLayout.onExtDocsLink = onExtDocsLink
