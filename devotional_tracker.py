import streamlit as st
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Devotional Tracker", layout="centered")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #F9F7F4;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stAppViewContainer"] { padding-top: 2rem; }
[data-testid="stHeader"]           { background: transparent; }
[data-testid="block-container"]    { max-width: 680px; padding: 0 1.5rem; }

h1 {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 300; font-size: 2.4rem;
    color: #1C1C1C; letter-spacing: 0.02em;
    margin-bottom: 0.1rem;
}
.subtitle {
    font-size: 0.78rem; color: #9A9A9A;
    letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 1.6rem;
}
.thin-rule { border: none; border-top: 1px solid #E5E1DC; margin: 1.2rem 0; }

.verse-block {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem; line-height: 1.7; color: #4A4A4A;
    border-left: 3px solid #2D6A4F;
    padding: 0.6rem 1rem; margin: 0.4rem 0 0.8rem 0;
    background: #F2FAF5; border-radius: 0 6px 6px 0;
}
.verse-ref { font-size: 0.75rem; color: #9A9A9A; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.3rem; }
.task-note { font-size: 0.82rem; color: #7A7A7A; line-height: 1.6; margin-top: 0.3rem; }

[data-testid="stExpander"] summary {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.92rem; font-weight: 500;
    color: #1C1C1C; letter-spacing: 0.01em;
}
[data-testid="stExpander"] {
    border: 1px solid #E5E1DC !important;
    border-radius: 10px !important;
    background: #FFFFFF; margin-bottom: 8px;
}

.pct-label {
    text-align: center;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem; color: #9A9A9A;
    letter-spacing: 0.08em;
    margin-top: -1rem; margin-bottom: 1rem;
}

/* Pill nav styles */
.pill-row {
    display: flex; gap: 10px;
    align-items: center; margin-bottom: 1.4rem;
    flex-wrap: wrap;
}
.pill-row a {
    display: inline-flex; align-items: center; justify-content: center;
    width: 46px; height: 46px; border-radius: 50%;
    font-size: 0.85rem; font-family: 'DM Sans', sans-serif;
    text-decoration: none;
    transition: transform .12s, box-shadow .12s;
}
.pill-row a:hover { transform: scale(1.12); box-shadow: 0 2px 14px rgba(0,0,0,.13); }
.pill-done    { background: #2D6A4F !important; color: #fff !important; border: 2px solid #2D6A4F !important; }
.pill-failed  { background: #C0392B !important; color: #fff !important; border: 2px solid #C0392B !important; }
.pill-future  { background: #EBEBEB !important; color: #ABABAB !important; border: 2px solid #EBEBEB !important; pointer-events: none; }
.pill-current { background: #fff    !important; color: #1C1C1C !important; border: 2.5px solid #1C1C1C !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
TASKS = ["Rooted Word", "The Deep Dive", "Fast & Focus", "Prayer Lab", "Community Seed"]

TASK_CONTENT = {
    "Rooted Word": {
        "verse": "I am the vine; you are the branches. If you remain in me and I in you, you will bear much fruit; apart from me you can do nothing.",
        "ref": "John 15:5 (NIV)",
        "note": "Read slowly. Let the words settle. Consider what it means to abide today.",
    },
    "The Deep Dive": {
        "note": "Pick one passage, one commentary, or one theological idea. Go deep rather than wide. Write a single sentence of insight in your journal.",
    },
    "Fast & Focus": {
        "note": "Skip one meal or social media block. Use that window to be present with God — even if only 10 minutes of stillness.",
    },
    "Prayer Lab": {
        "note": "Experiment with a prayer form: written, spoken, silent, intercessory. Log what you prayed and one thing you sensed.",
    },
    "Community Seed": {
        "note": "Encourage or serve one person today — a message, a kind act, a shared resource. Plant something in someone else's soil.",
    },
}

TOTAL_DAYS  = 7
CURRENT_DAY = 3   # ← change to reflect real "today" in production

# ── Session state ─────────────────────────────────────────────────────────────
if "active_day" not in st.session_state:
    st.session_state.active_day = CURRENT_DAY

if "tasks" not in st.session_state:
    st.session_state.tasks = {d: {t: False for t in TASKS} for d in range(1, TOTAL_DAYS + 1)}

if "demo_seeded" not in st.session_state:
    # Seed days 1-2 as fully complete for demo
    for past_day in [1, 2]:
        for t in TASKS:
            st.session_state.tasks[past_day][t] = True
    st.session_state.demo_seeded = True

# ── Read day from query param set by pill click ───────────────────────────────
qp = st.query_params
if "day" in qp:
    try:
        d = int(qp["day"])
        if 1 <= d <= TOTAL_DAYS:
            st.session_state.active_day = d
    except ValueError:
        pass

active = st.session_state.active_day

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("<h1>Devotional</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Daily Practice Tracker</p>', unsafe_allow_html=True)

# ── Pill nav (HTML <a> links — no st.button duplication) ──────────────────────
def pill_css_class(d):
    if d == active:
        return "pill-current"
    elif d < CURRENT_DAY:
        return "pill-done" if all(st.session_state.tasks[d].values()) else "pill-failed"
    elif d == CURRENT_DAY:
        return "pill-current"
    else:
        return "pill-future"

pills = '<div class="pill-row">'
for d in range(1, TOTAL_DAYS + 1):
    cls   = pill_css_class(d)
    href  = f"?day={d}"
    extra = ' tabindex="-1"' if cls == "pill-future" else ""
    pills += f'<a href="{href}" class="{cls}"{extra} title="Day {d}">{d}</a>'
pills += "</div>"

st.markdown(pills, unsafe_allow_html=True)

# ── Redemption banner ─────────────────────────────────────────────────────────
if active < CURRENT_DAY:
    missed = not all(st.session_state.tasks[active].values())
    if missed:
        st.markdown(f"""
        <div style="background:#FFF8F0;border:1px solid #F0D5B0;border-radius:10px;
                    padding:0.7rem 1rem;margin-bottom:0.8rem;
                    font-size:0.82rem;color:#8B5E2A;line-height:1.5;">
            📖 <strong>Day {active} — </strong>
            It's not too late. Read, reflect, and mark what you can.
            Grace covers the rest.
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='thin-rule'>", unsafe_allow_html=True)

# ── Progress circle ───────────────────────────────────────────────────────────
day_tasks = st.session_state.tasks[active]
completed  = sum(day_tasks.values())
total      = len(TASKS)
pct        = int(completed / total * 100)

fig = go.Figure(go.Pie(
    values=[max(completed, 0.001), total - completed],
    hole=0.72,
    marker_colors=["#2D6A4F", "#EAE8E4"],
    direction="clockwise",
    sort=False,
    textinfo="none",
    hoverinfo="skip",
))
fig.update_layout(
    showlegend=False,
    margin=dict(t=10, b=10, l=10, r=10),
    paper_bgcolor="rgba(0,0,0,0)",
    height=200,
    annotations=[dict(
        text=f"<b>{pct}%</b>",
        x=0.5, y=0.5,
        font=dict(size=28, color="#1C1C1C", family="Cormorant Garamond"),
        showarrow=False,
    )],
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.markdown(f'<p class="pct-label">Day {active} · {completed} of {total} tasks</p>', unsafe_allow_html=True)
st.markdown("<hr class='thin-rule'>", unsafe_allow_html=True)

# ── Accordions ────────────────────────────────────────────────────────────────
for task in TASKS:
    content = TASK_CONTENT[task]
    checked = st.session_state.tasks[active][task]
    icon    = "✓" if checked else "○"

    with st.expander(f"{icon}  {task}"):
        if "verse" in content:
            st.markdown(
                f'<div class="verse-block">{content["verse"]}'
                f'<div class="verse-ref">{content["ref"]}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown(f'<p class="task-note">{content["note"]}</p>', unsafe_allow_html=True)

        new_val = st.checkbox("Mark complete", value=checked, key=f"check_{active}_{task}")
        if new_val != checked:
            st.session_state.tasks[active][task] = new_val
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center;font-size:0.72rem;color:#C0BBB4;letter-spacing:0.1em;">'
    'DEVOTIONAL TRACKER · 7-DAY PRACTICE</p>',
    unsafe_allow_html=True,
)
