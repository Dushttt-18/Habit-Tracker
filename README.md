# 🌱 Habit Tracker

A clean, free habit & daily routine tracker built with Streamlit.

## Features
- ✅ Check off habits each day
- 🔥 Streak tracking (current + longest)
- 📅 30-day visual heatmap per habit
- 📊 Daily completion rate & stats
- ➕ Add / remove habits anytime
- 📆 View/edit any past date
- 💾 Data saved as local JSON (no database needed)

## Deploy FREE on Streamlit Community Cloud

1. **Fork or upload** this folder to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"**, pick your repo, set `app.py` as the main file.
4. Click **Deploy** — done! Your tracker is live at a free `*.streamlit.app` URL.

> Data is stored in `habits_data.json` in the app's working directory.  
> On Streamlit Cloud the file persists between sessions on the same deployment.

## Run locally

```bash
pip install streamlit
streamlit run app.py
```
