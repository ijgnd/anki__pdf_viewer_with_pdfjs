import aqt

from aqt.qt import qtmajor


# adjusted from bettersearch, adjusted from my half-baked ir add-on
def move_window(left, right, newpos):
    if qtmajor == 5:
        screen = aqt.mw.app.desktop().screenGeometry()
    else:
        screen = aqt.mw.screen().availableGeometry()
    width = screen.width()
    height = screen.height()
    rx = right.x()
    ry = right.y()
    rw = right.width()
    rh = right.height()
    lx = left.x()
    ly = left.y()
    lw = left.width()
    lh = left.height()
    if newpos == "side-by-side":
        if rx > lw:  # if there's enough space left of the right dialog, don't move right
                     # and just put the left dialog next to it.
            # try to level top of windows, doesn't really work on my computer?
            if (height-ry) > lh:
                ly = ry
            left.setGeometry(rx-lw, ly, lw, lh)
        elif lw + rw <= width:  # if there's enough space on the screen, if you move the right dialog
                               # move
            leftspace = (width - (lw+rw))/2
            # try to level top of windows, doesn't really work on my computer?
            if (height-ry) > lh:
                ly = ry
            left.setGeometry( leftspace,      ly, lw, lh)
            right.setGeometry(leftspace + lw, ry, rw, rh)
        else:  # total width over screen width: shrink and move
            # fully fixing is too complicated, just resize info box and move to left and hope for
            # the best
            if lw > 350:
                lw = 350
            # try to level top of windows, doesn't really work on my computer?
            if (height-ry) > lh:
                ly = ry
            left.setGeometry(  0, ly, lw, lh)
            right.setGeometry(rx, ry, rw, rh)
