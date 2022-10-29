import os

from aqt import mw


def gc(arg, fail=False):
    try:
        out = mw.addonManager.getConfig(__name__).get(arg, fail)
    except:
        return fail
    else:
        return out


def wc(arg, val):
    try:
        config = mw.addonManager.getConfig(__name__)
    except:
        return None
    else:
        if config:
            config[arg] = val
            mw.addonManager.writeConfig(__name__, config)


addon_path = os.path.dirname(__file__)
