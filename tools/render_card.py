"""Render a Scrollkind single-image post (1080x1350 PNG) from a JSON spec.

Usage: python3 tools/render_card.py spec.json out.png

spec.json:
{
  "bg": "ink" | "cream" | "coral" | "mint",
  "kicker": "TECH TIP",              # small label at top
  "headline": "Lock your WhatsApp with a PIN",
  "points": ["Open Settings → Account", "..."],   # 0-4 short lines
  "footer": "Save this & share it"   # optional
}
"""
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "brand" / "fonts"

INK, CREAM, CORAL, MINT = "#16213A", "#F6F1E7", "#E07A4F", "#7FD1BF"
THEMES = {
    "ink":   dict(bg=INK,   fg=CREAM, accent=CORAL, word1=CREAM, word2=CORAL),
    "cream": dict(bg=CREAM, fg=INK,   accent=CORAL, word1=INK,   word2=CORAL),
    "coral": dict(bg=CORAL, fg=INK,   accent=INK,   word1=INK,   word2=INK),
    "mint":  dict(bg=MINT,  fg=INK,   accent=INK,   word1=INK,   word2=CORAL),
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_html(spec: dict) -> str:
    t = THEMES[spec.get("bg", "ink")]
    points = "".join(
        f'<li><span class="dot"></span>{esc(p)}</li>' for p in spec.get("points", [])
    )
    footer = esc(spec.get("footer", ""))
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Fraunces; src: url('{(FONTS / "fraunces-latin-wght-normal.woff2").as_uri()}'); font-weight: 100 900; }}
@font-face {{ font-family: 'DM Sans'; src: url('{(FONTS / "DMSans.ttf").as_uri()}'); font-weight: 100 1000; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1350px; background:{t['bg']}; color:{t['fg']};
        font-family:'DM Sans', sans-serif; position:relative; overflow:hidden; }}
.top {{ position:absolute; top:90px; left:96px; right:96px; display:flex;
        justify-content:space-between; align-items:center; }}
.word {{ font-family:Fraunces; font-weight:700; font-size:44px; letter-spacing:-0.5px; }}
.word .a {{ color:{t['word1']}; }} .word .b {{ color:{t['word2']}; }}
.kicker {{ font-weight:700; font-size:26px; letter-spacing:4px; text-transform:uppercase;
           border:3px solid {t['fg']}; border-radius:999px; padding:12px 28px; }}
.spark {{ position:absolute; top:250px; right:140px; width:70px; height:70px; }}
.body {{ position:absolute; left:96px; right:96px; bottom:230px; }}
h1 {{ font-family:Fraunces; font-weight:800; font-size:104px; line-height:1.02;
      letter-spacing:-2px; margin-bottom:56px; }}
h1 .hl {{ color:{t['accent']}; }}
ul {{ list-style:none; }}
li {{ font-size:38px; line-height:1.35; margin-bottom:22px; display:flex; gap:24px; align-items:flex-start; }}
.dot {{ flex:none; width:18px; height:18px; border-radius:50%; background:{t['accent']}; margin-top:17px; }}
.bottom {{ position:absolute; left:96px; right:96px; bottom:96px; display:flex;
           justify-content:space-between; align-items:center; font-size:28px; }}
.pill {{ border:3px solid {t['fg']}; border-radius:999px; padding:14px 32px; font-weight:700; }}
</style></head><body>
<div class="top"><div class="word"><span class="a">Scroll</span><span class="b">kind</span></div>
<div class="kicker">{esc(spec.get('kicker', 'Tech news'))}</div></div>
<svg class="spark" viewBox="0 0 100 100"><path d="M50 0 C55 38 62 45 100 50 C62 55 55 62 50 100 C45 62 38 55 0 50 C38 45 45 38 50 0Z" fill="{MINT if spec.get('bg') != 'mint' else INK}"/></svg>
<div class="body"><h1>{spec['headline']}</h1><ul>{points}</ul></div>
<div class="bottom"><div>{footer}</div><div class="pill">@scrollkind_</div></div>
</body></html>"""


def main() -> None:
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2]).resolve()
    html_path = out.with_suffix(".html")
    html_path.write_text(build_html(spec))
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.goto(html_path.as_uri())
        page.wait_for_timeout(400)
        page.screenshot(path=str(out))
        browser.close()
    html_path.unlink()
    print(out)


if __name__ == "__main__":
    main()
