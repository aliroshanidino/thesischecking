"""Figure kit: inline Material Design icons + Chromium rendering to high-DPI PNG."""
import re, subprocess, json, os
ICON_DIR = '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/icons_dl/package/svg'
def icon(name, size=48, color='#203864', x=None, y=None):
    svg = open(f'{ICON_DIR}/{name}.svg').read()
    path = re.search(r' d="([^"]+)"', svg).group(1)
    if x is None:
        return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24"><path d="{path}" fill="{color}"/></svg>'
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24"><path d="{path}" fill="{color}"/></svg>'
FONT_CSS = "@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:ital,wght@0,600;1,400&display=swap'); .ss{font-family:'Source Sans 3',sans-serif} .sf{font-family:'Source Serif 4',serif}"
def render_html(html, out_png, width, height, scale=3):
    tmp = out_png.replace('.png', '.html'); open(tmp, 'w').write(html)
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();
    const p=await b.newPage({{viewport:{{width:{width},height:{height}}},deviceScaleFactor:{scale}}});
    await p.goto('file://{tmp}');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(1200);
    await p.screenshot({{path:'{out_png}',omitBackground:true,clip:{{x:0,y:0,width:{width},height:{height}}}}});await b.close();}})()"""
    r = subprocess.run(['node', '-e', js], capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr)
    return out_png

def icon_png(name, color, out, px=96):
    """Render one Material Design icon to a transparent PNG."""
    html = f'<!doctype html><html><body style="margin:0;background:transparent">{icon(name, px, color)}</body></html>'
    return render_html(html, out, px, px, 3)
