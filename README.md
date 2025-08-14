# 🏋️‍♂️ Workout Planner

A **Streamlit** web app that creates personalized workout plans tailored to your goals, fitness level, equipment, limitations, and available time.  
Whether you’re just starting out or have been training for years, **Workout Planner** makes structuring your week simple and effective.

---

## 🌐 Live Demo & Code
- **App:** https://workout-planner-wnwjbjprd23f55vusw3lav.streamlit.app/
- **Repo:** https://github.com/tushar-1803/Workout-planner

---

## 🚀 Features
- **Personalized plans** — adapts to your fitness level, goals (Strength / Hypertrophy / Conditioning / Mobility), equipment, limitations, and weekly time.
- **Smart plan builder** — balances movement patterns (push / pull / squat / hinge / core / mobility) and adjusts sets–reps–rest by goal & experience.
- **Exercise demos** — optional embedded YouTube videos via the YouTube Data API (securely loaded using Streamlit Secrets).
- **Clean UI** — dark, gym-inspired theme, user-friendly copy, and expandable day cards.
- **Exports** — download your plan as **CSV** or **Markdown**.
- **Plan Code** — regenerate the exact same plan later.

---

## 🧠 How It Works (Quick)
1. Choose your **goal**, **days/week**, **minutes/session**, **experience**, **equipment**, **limitations**, and optional **focus**.
2. The app builds a **weekly split** and assigns exercises for each day.
3. Sets/reps/rest are adjusted to your goal, or **timed circuits**/**holds** for conditioning/mobility.
4. Optional embedded **demo videos**.
5. Export your plan to CSV or Markdown.

---

## 🛠 Tech Stack
- **App Framework:** Python + Streamlit
- **Data Handling:** Pandas
- **Video Integration:** YouTube Data API v3
- **Deployment:** Streamlit Community Cloud
- **Secrets Management:** Streamlit Secrets (never committed to GitHub)



## 📦 Installation & Running Locally

bash
# 1) Clone this repository
git clone https://github.com/tushar-1803/Workout-planner.git
cd Workout-planner

# 2) (Recommended) Create & activate a virtual environment
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Add your YouTube API key 
# Create .streamlit/secrets.toml and add:
# YT_API_KEY = "YOUR_OWN_API_KEY"

# 5) Run the app
streamlit run app.py
