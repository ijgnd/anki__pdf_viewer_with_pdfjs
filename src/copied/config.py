import os

from aqt import mw


def gc(arg, fail=False):
    try:
        out = mw.addonManager.getConfig(__name__).get(arg, fail)
    except:
        return fail
    else:
        return out


addon_path = os.path.dirname(__file__)

pycmd_string = "open_external_addon"
