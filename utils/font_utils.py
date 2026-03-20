from matplotlib import rcParams

def configure_fonts():
    try:
        rcParams["font.sans-serif"] = ["CascadiaMono", "HarmonyOS Sans SC"]
        rcParams["font.size"] = 12
    except Exception:
        try:
            rcParams["font.sans-serif"] = ["arial", "msyh"]
        except Exception as e:
            print(f"字体设置错误: {e}")
            return False
    rcParams["axes.unicode_minus"] = False
    return True