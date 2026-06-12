import streamlit as st
import json
import os
from datetime import date, timedelta, datetime
import calendar

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Habit Tracker",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background-color: #ccf5c6;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #161b27;
    border-right: 1px solid #1e2a3a;
}

/* Headings */
h1, h2, h3 {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    color: #e8f0fe;
    letter-spacing: -0.02em;
}

/* Cards */
.habit-card {
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: border-color 0.2s;
}
.habit-card:hover {
    border-color: #3b5bdb;
}
.habit-card.done {
    border-color: #2d6a4f;
    background: #0d2818;
}
.habit-name {
    font-size: 1rem;
    font-weight: 500;
    color: #c9d1e0;
}
.habit-streak {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #f4a261;
    background: #2a1f0a;
    padding: 2px 8px;
    border-radius: 20px;
}
.habit-done-badge {
    font-size: 0.78rem;
    color: #52b788;
    background: #0d2818;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid #2d6a4f;
}

/* Stat cards */
.stat-card {
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.stat-num {
    font-family: 'DM Mono', monospace;
    font-size: 2.2rem;
    font-weight: 500;
    color: #74b9ff;
    line-height: 1;
    margin-bottom: 4px;
}
.stat-label {
    font-size: 0.8rem;
    color: #6b7a99;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Heatmap cell */
.hm-cell {
    display: inline-block;
    width: 14px;
    height: 14px;
    border-radius: 3px;
    margin: 1px;
}

/* Section header */
.section-eyebrow {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #3b5bdb;
    font-weight: 600;
    margin-bottom: 4px;
}

/* Progress bar override */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #3b5bdb, #74b9ff);
    border-radius: 4px;
}

/* Buttons */
.stButton > button {
    background: #1c2c4a;
    color: #74b9ff;
    border: 1px solid #2a3f65;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    transition: all 0.15s;
}
.stButton > button:hover {
    background: #243355;
    border-color: #3b5bdb;
    color: #a5c8ff;
}

/* Delete button */
.stButton > button[kind="secondary"] {
    background: #1e1520;
    color: #e07070;
    border-color: #3a2030;
}

/* Divider */
hr {
    border-color: #1e2a3a;
}

/* Checkbox */
.stCheckbox label {
    color: #c9d1e0 !important;
    font-family: 'DM Sans', sans-serif;
}

/* Input */
.stTextInput > div > div > input {
    background: #1a2235;
    border: 1px solid #2a3a55;
    color: #e8f0fe;
    border-radius: 8px;
}
.stTextInput > div > div > input:focus {
    border-color: #3b5bdb;
    box-shadow: 0 0 0 2px rgba(59,91,219,0.2);
}
</style>
""", unsafe_allow_html=True)

# ── Data helpers ──────────────────────────────────────────────────────────────
DATA_FILE = "habits_data.json"

DEFAULT_HABITS = [
    {"name": "Morning meditation", "emoji": "🧘"},
    {"name": "Exercise", "emoji": "💪"},
    {"name": "Read 20 pages", "emoji": "📖"},
    {"name": "Drink 8 glasses of water", "emoji": "💧"},
    {"name": "No social media before noon", "emoji": "📵"},
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "habits": [
            {"id": i, "name": h["name"], "emoji": h["emoji"], "created": str(date.today())}
            for i, h in enumerate(DEFAULT_HABITS)
        ],
        "completions": {}   # {"2025-06-10": [0, 2, 3], ...}
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_streak(habit_id, completions):
    """Count current consecutive-day streak."""
    streak = 0
    check = date.today()
    while True:
        key = str(check)
        if key in completions and habit_id in completions[key]:
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return streak

def get_longest_streak(habit_id, completions):
    if not completions:
        return 0
    all_dates = sorted(completions.keys())
    best = cur = 0
    prev = None
    for d_str in all_dates:
        if habit_id in completions[d_str]:
            d = date.fromisoformat(d_str)
            if prev and (d - prev).days == 1:
                cur += 1
            else:
                cur = 1
            best = max(best, cur)
            prev = d
        else:
            prev = None
    return best

def completion_rate_7d(habit_id, completions):
    done = sum(
        1 for i in range(7)
        if str(date.today() - timedelta(days=i)) in completions
        and habit_id in completions[str(date.today() - timedelta(days=i))]
    )
    return done / 7

# ── Load state ────────────────────────────────────────────────────────────────
data = load_data()
habits = data["habits"]
completions = data["completions"]
today_key = str(date.today())
today_done = set(completions.get(today_key, []))

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌱 Habit Tracker")
    st.markdown(f"<div style='color:#6b7a99;font-size:0.85rem;margin-bottom:1.5rem;'>{date.today().strftime('%A, %B %d %Y')}</div>", unsafe_allow_html=True)

    st.markdown("### Add Habit")
    new_emoji = st.text_input("Emoji", value="✨", max_chars=2, key="new_emoji")
    new_name = st.text_input("Habit name", placeholder="e.g. Journal for 5 min", key="new_name")
    if st.button("＋ Add habit", use_container_width=True):
        if new_name.strip():
            new_id = max((h["id"] for h in habits), default=-1) + 1
            habits.append({"id": new_id, "name": new_name.strip(), "emoji": new_emoji, "created": str(date.today())})
            data["habits"] = habits
            save_data(data)
            st.success("Habit added!")
            st.rerun()
        else:
            st.warning("Enter a habit name.")

    st.divider()

    st.markdown("### Delete Habit")
    if habits:
        del_choice = st.selectbox(
            "Select to remove",
            options=[h["id"] for h in habits],
            format_func=lambda i: next(f"{h['emoji']} {h['name']}" for h in habits if h["id"] == i),
            key="del_choice"
        )
        if st.button("🗑 Remove", use_container_width=True):
            habits = [h for h in habits if h["id"] != del_choice]
            data["habits"] = habits
            save_data(data)
            st.rerun()

    st.divider()
    st.markdown("<div style='color:#3d4f6e;font-size:0.75rem;text-align:center;'>Data saved locally · Free forever</div>", unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────────────────────
col_title, col_date = st.columns([3, 1])
with col_title:
    st.markdown("# Today's Habits")
with col_date:
    selected_date = st.date_input("Date", value=date.today(), label_visibility="collapsed")

selected_key = str(selected_date)
selected_done = set(completions.get(selected_key, []))
is_today = selected_date == date.today()

# ── Stats row ─────────────────────────────────────────────────────────────────
total_habits = len(habits)
done_today = len([h for h in habits if h["id"] in selected_done])
total_all_time = sum(len(v) for v in completions.values())
all_streaks = [get_streak(h["id"], completions) for h in habits]
best_streak_now = max(all_streaks) if all_streaks else 0

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-num">{done_today}/{total_habits}</div>
        <div class="stat-label">Done today</div>
    </div>""", unsafe_allow_html=True)
with s2:
    pct = int(done_today / total_habits * 100) if total_habits else 0
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-num">{pct}%</div>
        <div class="stat-label">Completion rate</div>
    </div>""", unsafe_allow_html=True)
with s3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-num">{best_streak_now}</div>
        <div class="stat-label">Best streak today</div>
    </div>""", unsafe_allow_html=True)
with s4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-num">{total_all_time}</div>
        <div class="stat-label">Total completions</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Progress bar ──────────────────────────────────────────────────────────────
if total_habits:
    st.markdown(f"<div class='section-eyebrow'>Daily Progress</div>", unsafe_allow_html=True)
    st.progress(done_today / total_habits)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Habit checklist ───────────────────────────────────────────────────────────
st.markdown(f"<div class='section-eyebrow'>{selected_date.strftime('%A, %b %d')}</div>", unsafe_allow_html=True)

if not habits:
    st.info("No habits yet — add one in the sidebar!")
else:
    changed = False
    for habit in habits:
        hid = habit["id"]
        is_done = hid in selected_done
        streak = get_streak(hid, completions)
        rate = completion_rate_7d(hid, completions)

        col_check, col_info, col_meta = st.columns([0.08, 0.72, 0.20])
        with col_check:
            new_val = st.checkbox("", value=is_done, key=f"cb_{hid}_{selected_key}")
        with col_info:
            badge_html = f'<span class="habit-done-badge">✓ Done</span>' if is_done else ''
            st.markdown(
                f'<div style="padding-top:6px;">'
                f'<span class="habit-name">{habit["emoji"]} {habit["name"]}</span> {badge_html}'
                f'</div>',
                unsafe_allow_html=True
            )
        with col_meta:
            if streak > 0:
                st.markdown(f'<div style="padding-top:6px;text-align:right;"><span class="habit-streak">🔥 {streak}d</span></div>', unsafe_allow_html=True)

        if new_val != is_done:
            if new_val:
                selected_done.add(hid)
            else:
                selected_done.discard(hid)
            completions[selected_key] = list(selected_done)
            data["completions"] = completions
            save_data(data)
            changed = True

    if changed:
        st.rerun()

# ── Weekly heatmap per habit ──────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("## 📅 Last 30 Days")

days_30 = [date.today() - timedelta(days=i) for i in range(29, -1, -1)]
week_labels = []
prev_week = None
for d in days_30:
    wk = d.isocalendar()[1]
    if wk != prev_week:
        week_labels.append(d.strftime("W%W"))
        prev_week = wk

for habit in habits:
    hid = habit["id"]
    cells = ""
    for d in days_30:
        key = str(d)
        done = key in completions and hid in completions[key]
        color = "#2d6a4f" if done else "#1a2235"
        title = f"{d.strftime('%b %d')}: {'✓' if done else '✗'}"
        cells += f'<span class="hm-cell" style="background:{color};" title="{title}"></span>'

    longest = get_longest_streak(hid, completions)
    cur_streak = get_streak(hid, completions)
    rate_30 = sum(
        1 for d in days_30
        if str(d) in completions and hid in completions[str(d)]
    ) / 30 * 100

    st.markdown(
        f'<div style="margin-bottom:18px;">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">'
        f'<span style="color:#c9d1e0;font-size:0.9rem;font-weight:500;">{habit["emoji"]} {habit["name"]}</span>'
        f'<span style="color:#6b7a99;font-size:0.75rem;font-family:\'DM Mono\',monospace;">'
        f'🔥 {cur_streak}d &nbsp; best {longest}d &nbsp; {rate_30:.0f}% rate'
        f'</span></div>'
        f'<div>{cells}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#2d3a50;font-size:0.78rem;'>Built with Streamlit · Free to deploy on Streamlit Community Cloud</div>",
    unsafe_allow_html=True
)
