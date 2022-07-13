from aqt import mw

def gc(arg, fail=False):
    try:
        out = mw.addonManager.getConfig(__name__).get(arg, fail)
    except:
        return None
    else:
        return out
