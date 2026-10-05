"""Visual layer for the Streamlit app: global glass theme, the 3D heart hero, vital cards and chart styling.

Design notes
- Palette "night lagoon": deep ocean background with slow aurora light, frosted-glass surfaces,
  mint for healthy readings and a coral pulse colour for the heart.
- One bold element: a 3D glass heart that beats at the patient's latest logged heart rate.
  Everything else stays quiet so the numbers are easy to read.
- Respects prefers-reduced-motion (the heart stops beating, the aurora stops drifting).
"""

from __future__ import annotations

import html
import json

import streamlit as st
import streamlit.components.v1 as components

ABYSS = "#071A2C"
LAGOON = "#0F3D57"
MINT = "#7FE3D0"
PULSE = "#FF5C7A"
MIST = "#E6F1F5"
MUTED = "#9DB7C6"

SEVERITY = {
    "normal": {"label": "Normal", "color": MINT},
    "watch": {"label": "Watch", "color": "#FFC857"},
    "high": {"label": "High", "color": "#FF9150"},
    "urgent": {"label": "Urgent", "color": "#FF4D6D"},
}

# Fonts are self-hosted from ./static (Streamlit static serving) so no third party sees patient visits.
FONT_FACES = "".join(
    f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{w};font-display:swap;"
    f"src:url('/app/static/fonts/{family.lower()}-latin-{w}-normal.woff2') format('woff2');}}"
    for family, weights in (("Sora", (400, 600, 700)), ("Figtree", (400, 500, 600)))
    for w in weights
)
THREE_CDNS = [
    "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",
    "https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js",
]

CSS = f"""
<style>
{FONT_FACES}
:root {{
  --abyss: {ABYSS}; --lagoon: {LAGOON}; --mint: {MINT}; --pulse: {PULSE}; --mist: {MIST}; --muted: {MUTED};
  --glass: rgba(255,255,255,0.06); --glass-strong: rgba(255,255,255,0.10); --edge: rgba(255,255,255,0.14);
  --radius-l: 22px; --radius-m: 14px; --radius-s: 10px;
}}
html, body, [class*="css"], .stApp, .stMarkdown, button, input, textarea, select {{ font-family: 'Figtree', sans-serif; }}
h1, h2, h3, h4, [data-testid="stMetricValue"] {{ font-family: 'Sora', sans-serif !important; letter-spacing: -0.02em; }}
h1 {{ font-weight: 700 !important; }}
h2, h3 {{ font-weight: 600 !important; }}

/* Background: deep water with two slow aurora lights */
.stApp {{
  background: radial-gradient(1200px 700px at 85% -10%, rgba(127,227,208,0.16), transparent 60%),
              radial-gradient(900px 600px at -10% 110%, rgba(255,92,122,0.12), transparent 60%),
              linear-gradient(160deg, var(--abyss) 0%, #0A2740 55%, var(--abyss) 100%);
  background-attachment: fixed; color: var(--mist);
}}
.stApp::before {{
  content: ""; position: fixed; inset: -20%; pointer-events: none; z-index: 0;
  background: conic-gradient(from 200deg at 60% 40%, transparent 0deg, rgba(127,227,208,0.07) 60deg, transparent 140deg,
              rgba(80,140,255,0.06) 220deg, transparent 300deg);
  filter: blur(60px); animation: drift 38s linear infinite;
}}
@keyframes drift {{ to {{ transform: rotate(360deg); }} }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stBottom"], [data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] {{ background: transparent !important; }}
[data-testid="stChatInput"] {{ background: rgba(7,26,44,0.6) !important; backdrop-filter: blur(16px); border-radius: 999px !important; }}
.block-container {{ padding-top: 2rem; max-width: 1240px; }}

/* Sidebar as a frosted pane */
[data-testid="stSidebar"] {{
  background: rgba(7,26,44,0.55) !important; backdrop-filter: blur(22px) saturate(140%);
  -webkit-backdrop-filter: blur(22px) saturate(140%); border-right: 1px solid var(--edge);
}}
[data-testid="stSidebar"] h1 {{ font-size: 1.35rem; }}

/* Glass surfaces for Streamlit containers */
[data-testid="stExpander"] details, [data-testid="stForm"], [data-testid="stChatMessage"],
[data-testid="stDataFrame"], .stTabs [data-baseweb="tab-panel"] {{
  background: var(--glass) !important; border: 1px solid var(--edge) !important; border-radius: var(--radius-m) !important;
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
}}
[data-testid="stExpander"] summary:hover {{ color: var(--mint); }}
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
.stTabs [data-baseweb="tab"] {{ border-radius: 999px; padding: 6px 16px; background: var(--glass); }}
.stTabs [aria-selected="true"] {{ background: rgba(127,227,208,0.18) !important; color: var(--mint) !important; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none; }}

/* Inputs and buttons */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"], .stNumberInput input {{
  background: rgba(255,255,255,0.05) !important; border-radius: var(--radius-s) !important; border-color: var(--edge) !important;
}}
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
  border-radius: 999px; border: 1px solid var(--edge); background: var(--glass-strong); color: var(--mist);
  transition: background .2s, border-color .2s, transform .1s;
}}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {{
  border-color: var(--mint); color: var(--mint);
}}
.stButton > button:active {{ transform: scale(0.98); }}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primaryFormSubmit"] {{
  background: linear-gradient(135deg, #2BB3A3, #1C7FA6); border: none; color: white; font-weight: 600;
  box-shadow: 0 8px 24px -10px rgba(43,179,163,0.8);
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, #FF5C7A, #E0365A); box-shadow: 0 10px 30px -12px rgba(255,92,122,0.9);
}}
button:focus-visible, input:focus-visible, [role="radio"]:focus-visible {{ outline: 2px solid var(--mint) !important; outline-offset: 2px; }}

/* Our own components */
.glass {{
  background: linear-gradient(145deg, rgba(255,255,255,0.10), rgba(255,255,255,0.03));
  border: 1px solid var(--edge); border-radius: var(--radius-l); padding: 18px 20px;
  backdrop-filter: blur(18px) saturate(140%); -webkit-backdrop-filter: blur(18px) saturate(140%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.12), 0 20px 40px -24px rgba(0,0,0,0.6);
}}
.vital {{ position: relative; overflow: hidden; min-height: 168px; }}
.vital .orb {{ position: absolute; width: 170px; height: 170px; right: -55px; top: -65px; border-radius: 50%; pointer-events: none; }}
.vital .label {{ color: var(--muted); font-size: .9rem; }}
.vital .value {{ font-family: 'Sora', sans-serif; font-size: 2.1rem; font-weight: 600; line-height: 1.15; margin-top: 6px; }}
.vital .unit {{ font-size: .95rem; color: var(--muted); margin-left: 4px; font-weight: 400; }}
.vital .foot {{ display: flex; justify-content: space-between; align-items: end; margin-top: 10px; gap: 8px; }}
.pill {{ display: inline-flex; align-items: center; gap: 7px; padding: 3px 11px; border-radius: 999px; font-size: .8rem;
  border: 1px solid; font-weight: 600; }}
.pill i {{ width: 7px; height: 7px; border-radius: 50%; display: inline-block; }}
.category {{ color: var(--muted); font-size: .82rem; margin-top: 8px; }}
.med-row {{ display: flex; align-items: center; gap: 14px; padding: 10px 4px; border-bottom: 1px solid rgba(255,255,255,0.07); }}
.med-row:last-child {{ border-bottom: none; }}
.med-time {{ font-family: 'Sora', sans-serif; font-weight: 600; min-width: 58px; color: var(--mint); }}
.med-name {{ flex: 1; }}
.med-dose {{ color: var(--muted); }}
.state {{ font-size: .8rem; padding: 2px 10px; border-radius: 999px; background: rgba(255,255,255,0.08); }}
.state.taken {{ color: var(--mint); }} .state.skipped {{ color: var(--muted); }} .state.pending {{ color: #FFC857; }}
.low {{ color: #FF9150; font-size: .8rem; }}
.page-title {{ margin: 0 0 4px 0; }}
.subtle {{ color: var(--muted); }}
@media (prefers-reduced-motion: reduce) {{ .stApp::before {{ animation: none; }} }}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def page_title(title: str, subtitle: str = "") -> None:
    sub = f'<div class="subtle">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<h1 class="page-title">{html.escape(title)}</h1>{sub}', unsafe_allow_html=True)


def sparkline(values: list[float], color: str, width: int = 110, height: int = 34) -> str:
    if len(values) < 2:
        return ""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    step = width / (len(values) - 1)
    pts = [(i * step, height - 3 - (v - lo) / span * (height - 6)) for i, v in enumerate(values)]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    area = f"{path} L{width},{height} L0,{height} Z"
    gid = f"g{abs(hash((tuple(values), color))) % 10**8}"
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" aria-hidden="true">'
        f'<defs><linearGradient id="{gid}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{color}" stop-opacity=".35"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
        f'<path d="{area}" fill="url(#{gid})"/><path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
        f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3" fill="{color}"/></svg>'
    )


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def pill(severity: str) -> str:
    c = SEVERITY[severity]["color"]
    return (
        f'<span class="pill" style="color:{c};background:{_rgba(c, 0.16)};border-color:{_rgba(c, 0.45)}">'
        f'<i style="background:{c};box-shadow:0 0 8px {c}"></i>{SEVERITY[severity]["label"]}</span>'
    )


def vital_card(label: str, value: str, unit: str, severity: str, category: str, history: list[float]) -> str:
    sev = SEVERITY[severity]
    cat = "" if category == "Normal" else f'<div class="category">{html.escape(category)}</div>'
    return (
        f'<div class="glass vital"><div class="orb" style="background:radial-gradient(circle,{_rgba(sev["color"], 0.45)} 0%,transparent 70%)"></div>'
        f'<div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(value)}<span class="unit">{html.escape(unit)}</span></div>'
        f'<div class="foot">{pill(severity)}{sparkline(history, sev["color"])}</div>{cat}</div>'
    )


def med_rows(meds: list[dict]) -> str:
    if not meds:
        return '<div class="subtle">No medications scheduled. Add one on the Medications page.</div>'
    rows = []
    for m in meds:
        state = m["status_today"]
        low = f'<span class="low">{m["stock"]} left</span>' if m["low_stock"] else ""
        rows.append(
            f'<div class="med-row"><span class="med-time">{m["schedule_time"]}</span>'
            f'<span class="med-name">{html.escape(m["name"])} <span class="med-dose">{html.escape(m["dosage"])}</span></span>'
            f'{low}<span class="state {state}">{state.capitalize()}</span></div>'
        )
    return '<div class="glass">' + "".join(rows) + "</div>"


def heart_hero(name: str, bpm: int | None, status: str | None, headline: str) -> None:
    """3D glass heart (three.js) that beats at the latest logged heart rate, with the greeting beside it."""
    data = json.dumps(
        {
            "bpm": bpm or 70,
            "hasReading": bpm is not None,
            "color": SEVERITY[status]["color"] if status else MINT,
            "status": SEVERITY[status]["label"] if status else "",
            "name": name,
            "headline": headline,
        }
    )
    components.html(
        f"""
<!doctype html><html><head>
<style>
  {FONT_FACES}
  html,body{{margin:0;height:100%;background:transparent;overflow:hidden;font-family:'Figtree',sans-serif;color:{MIST}}}
  .wrap{{position:relative;height:100%;display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);align-items:center;
        border-radius:26px;border:1px solid rgba(255,255,255,.14);
        background:linear-gradient(135deg,rgba(255,255,255,.10),rgba(255,255,255,.02));
        box-shadow:inset 0 1px 0 rgba(255,255,255,.15)}}
  .copy{{padding:28px 34px;z-index:2}}
  .hello{{color:{MUTED};font-size:15px}}
  h1{{font-family:'Sora',sans-serif;font-weight:700;font-size:34px;line-height:1.1;margin:6px 0 14px;letter-spacing:-.02em}}
  .bpm{{display:flex;align-items:baseline;gap:8px}}
  .bpm b{{font-family:'Sora',sans-serif;font-size:52px;font-weight:600;color:{PULSE};line-height:1}}
  .bpm span{{color:{MUTED}}}
  .status{{display:inline-block;margin-top:12px;padding:4px 12px;border-radius:999px;font-size:13px;
          border:1px solid var(--c);color:var(--c);background:color-mix(in srgb,var(--c) 15%,transparent)}}
  canvas{{position:absolute;right:0;top:0;width:55%!important;height:100%!important}}
  @media (max-width:640px){{.wrap{{grid-template-columns:1fr}} canvas{{opacity:.45;width:100%!important}} h1{{font-size:26px}}}}
</style></head><body>
<div class="wrap"><div class="copy" id="copy"></div></div>
<script>
const D = {data};
function loadThree(urls, done) {{
  if (!urls.length) return done();
  const el = document.createElement('script'); el.src = urls[0];
  el.onload = done; el.onerror = () => loadThree(urls.slice(1), done);
  document.head.appendChild(el);
}}
const copy = document.getElementById('copy');
const esc = s => s.replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
copy.innerHTML = `<div class="hello">Hello, ${{esc(D.name)}}</div><h1>${{esc(D.headline)}}</h1>` +
  (D.hasReading ? `<div class="bpm"><b id="n">${{D.bpm}}</b><span>bpm resting heart rate</span></div>` +
                  `<div class="status" style="--c:${{D.color}}">Latest reading: ${{esc(D.status)}}</div>`
                : `<div class="hello">Log your first reading to see your heart beat here.</div>`);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
loadThree({json.dumps(THREE_CDNS)}, () => {{
if (window.THREE) {{
  const wrap = document.querySelector('.wrap');
  const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  wrap.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
  camera.position.set(0, 0, 9);

  const s = new THREE.Shape();
  s.moveTo(0, 0.5); s.bezierCurveTo(0, 0.5, -0.4, 1.4, -1.4, 1.4); s.bezierCurveTo(-2.9, 1.4, -2.9, -0.4, -2.9, -0.4);
  s.bezierCurveTo(-2.9, -1.5, -1.9, -2.7, 0, -3.7); s.bezierCurveTo(1.9, -2.7, 2.9, -1.5, 2.9, -0.4);
  s.bezierCurveTo(2.9, -0.4, 2.9, 1.4, 1.4, 1.4); s.bezierCurveTo(0.4, 1.4, 0, 0.5, 0, 0.5);
  const geo = new THREE.ExtrudeGeometry(s, {{depth: 1.1, bevelEnabled: true, bevelSegments: 12, steps: 2, bevelSize: 0.55, bevelThickness: 0.6, curveSegments: 48}});
  geo.center();
  const mat = new THREE.MeshPhysicalMaterial({{color: new THREE.Color('#E0203F'), roughness: 0.16, metalness: 0.0,
    clearcoat: 1, clearcoatRoughness: 0.06, transmission: 0.12, transparent: true, opacity: 0.96, reflectivity: 0.5,
    emissive: new THREE.Color('#3D0410'), emissiveIntensity: 0.6}});
  const heart = new THREE.Mesh(geo, mat);
  heart.scale.setScalar(0.62);
  const group = new THREE.Group(); group.add(heart); scene.add(group);

  // soft halo behind the heart
  const halo = new THREE.Mesh(new THREE.CircleGeometry(3.4, 64),
    new THREE.MeshBasicMaterial({{color: new THREE.Color('{PULSE}'), transparent: true, opacity: 0.10}}));
  halo.position.z = -2; scene.add(halo);

  scene.add(new THREE.AmbientLight(0xffd6dd, 0.22));
  const key = new THREE.PointLight(0xffffff, 1.4); key.position.set(4, 5, 8); scene.add(key);
  const rim = new THREE.PointLight(new THREE.Color('{MINT}'), 1.3); rim.position.set(-6, -2, 3); scene.add(rim);
  const fill = new THREE.PointLight(0x6fa8ff, 0.8); fill.position.set(0, -6, 4); scene.add(fill);

  function resize() {{
    const w = renderer.domElement.clientWidth, h = renderer.domElement.clientHeight;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }}
  addEventListener('resize', resize); resize();
  let mx = 0, my = 0;
  addEventListener('pointermove', e => {{ mx = (e.clientX / innerWidth - .5); my = (e.clientY / innerHeight - .5); }});

  const period = 60 / Math.max(30, Math.min(200, D.bpm));
  const t0 = performance.now();
  function beat(t) {{
    // "lub-dub": a strong contraction followed by a smaller one, then rest
    const p = (t % period) / period;
    const pulse = (x, c, w) => Math.exp(-Math.pow((x - c) / w, 2));
    return 1 + 0.085 * pulse(p, 0.08, 0.045) + 0.045 * pulse(p, 0.26, 0.05);
  }}
  function frame(now) {{
    const t = (now - t0) / 1000;
    const k = reduce ? 1 : beat(t);
    heart.scale.setScalar(0.62 * k);
    halo.scale.setScalar(0.9 + (k - 1) * 4);
    halo.material.opacity = 0.08 + (k - 1) * 1.2;
    group.rotation.y += ((reduce ? 0 : Math.sin(t * 0.5) * 0.35) + mx * 0.8 - group.rotation.y) * 0.05;
    group.rotation.x += (my * 0.5 - group.rotation.x) * 0.05;
    renderer.render(scene, camera);
    if (!reduce) requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);
}}
}});
</script></body></html>
""",
        height=270,
    )


def style_figure(fig, height: int = 330):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)",
        font=dict(family="Figtree, sans-serif", color=MIST, size=13),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None, bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=LAGOON, font_family="Figtree"),
        colorway=[MINT, PULSE, "#7AA9FF", "#FFC857", "#C79BFF"],
    )
    fig.update_xaxes(showgrid=False, color=MUTED, title=None)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", color=MUTED, zeroline=False)
    palette = [MINT, PULSE, "#7AA9FF", "#FFC857", "#C79BFF"]
    for i, trace in enumerate(fig.data):
        c = palette[i % len(palette)]
        trace.update(line=dict(width=3, shape="spline", color=c), marker=dict(size=7, color=c))
        if getattr(trace, "fill", None) in ("tozeroy", "tonexty"):
            trace.update(fillcolor=_rgba(c, 0.15))
    return fig
