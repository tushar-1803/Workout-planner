import random
from typing import List, Dict, Optional
import streamlit as st
import pandas as pd

# ================================
# App Config & Global Styles
# ================================
st.set_page_config(page_title="Custom Workout Planner", page_icon="💪", layout="wide")

st.markdown("""
<style>
/* page width + padding */
.main .block-container {max-width: 1100px; padding-top: 2rem; padding-bottom: 2rem;}
/* gradient headline */
.hero-title {
  font-size: 2.4rem; font-weight: 800; letter-spacing: .3px;
  background: linear-gradient(90deg,#E6EDF3 0%, #4ADE80 50%, #60A5FA 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
  margin: 0 0 .25rem 0;
}
/* subhead */
.hero-sub { color: #B9C4D1; font-size: 1rem; margin-bottom: 1rem;}
/* badges */
.badge {display:inline-block; padding:.25rem .6rem; border-radius:999px; background:#1C2541;
  margin-right:.35rem; font-size:.8rem; color:#E6EDF3; border:1px solid rgba(255,255,255,.06);}
.badge + .badge {margin-left:.25rem;}
/* cards */
.card {border-radius:16px; padding:14px 16px; background:#1C2541; border:1px solid rgba(255,255,255,.06); margin-bottom:10px;}
.card h4{margin:0 0 .25rem 0; font-size:1rem;}
.card small{color:#9FB0C3;}
/* nicer buttons */
.stDownloadButton button, .stButton button {border-radius:999px; padding:.6rem 1rem; font-weight:700;}
/* sidebar spacing */
[data-testid="stSidebar"] .block-container {padding-top: 1rem;}
/* captions a bit brighter */
.css-1q1n0ol, .stMarkdown p small, .stMarkdown em {color:#9FB0C3;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">Custom Workout Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Build a weekly plan around <b>your</b> goal, time, and equipment. Toggle videos for quick exercise demos.</div>', unsafe_allow_html=True)
st.markdown(
    '<span class="badge">💪 Strength</span><span class="badge">🌟 Hypertrophy</span>'
    '<span class="badge">🔥 Conditioning</span><span class="badge">🧘 Mobility</span>',
    unsafe_allow_html=True
)
st.write("")

# ================================
# Exercise Library
# ================================
# pattern: 'squat' | 'hinge' | 'lunge' | 'push' | 'vertical_push' | 'pull' | 'vertical_pull' | 'core' | 'carry' | 'mobility'
# equipment: 'bodyweight', 'dumbbells', 'barbell', 'kettlebell', 'bands', 'pullup_bar', 'machines'
# contraindications: 'knee', 'shoulder_overhead', 'lumbar_flexion', 'wrist', 'impact'
EXERCISES: List[Dict] = [
    # Lower body
    {"name": "Back Squat", "pattern": "squat", "equipment": ["barbell"], "level_min": "intermediate",
     "contra": ["knee"], "goal_tags": ["strength", "hypertrophy"]},
    {"name": "Goblet Squat", "pattern": "squat", "equipment": ["dumbbells"], "level_min": "beginner",
     "contra": ["knee"], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Bodyweight Squat", "pattern": "squat", "equipment": ["bodyweight"], "level_min": "beginner",
      "contra": ["knee"], "goal_tags": ["general", "fatloss", "endurance"]},
    {"name": "Romanian Deadlift", "pattern": "hinge", "equipment": ["barbell", "dumbbells"], "level_min": "beginner",
     "contra": ["lumbar_flexion"], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Conventional Deadlift", "pattern": "hinge", "equipment": ["barbell"], "level_min": "intermediate",
     "contra": ["lumbar_flexion"], "goal_tags": ["strength", "hypertrophy"]},
    {"name": "Hip Thrust", "pattern": "hinge", "equipment": ["barbell", "dumbbells"], "level_min": "beginner",
     "contra": [], "goal_tags": ["hypertrophy", "general"]},
    {"name": "Kettlebell Swing", "pattern": "hinge", "equipment": ["kettlebell"], "level_min": "beginner",
     "contra": ["lumbar_flexion", "impact"], "goal_tags": ["fatloss", "endurance", "general"]},
    {"name": "Walking Lunge", "pattern": "lunge", "equipment": ["bodyweight", "dumbbells"], "level_min": "beginner",
     "contra": ["knee", "impact"], "goal_tags": ["hypertrophy", "general", "fatloss"]},
    {"name": "Bulgarian Split Squat", "pattern": "lunge", "equipment": ["bodyweight", "dumbbells"], "level_min": "intermediate",
     "contra": ["knee"], "goal_tags": ["hypertrophy", "general"]},
    {"name": "Step-up", "pattern": "lunge", "equipment": ["bodyweight", "dumbbells"], "level_min": "beginner",
     "contra": ["knee", "impact"], "goal_tags": ["general", "hypertrophy"]},

    # Push
    {"name": "Bench Press", "pattern": "push", "equipment": ["barbell"], "level_min": "intermediate",
     "contra": ["wrist"], "goal_tags": ["strength", "hypertrophy"]},
    {"name": "Dumbbell Bench Press", "pattern": "push", "equipment": ["dumbbells"], "level_min": "beginner",
      "contra": ["wrist"], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Push-up", "pattern": "push", "equipment": ["bodyweight"], "level_min": "beginner",
     "contra": ["wrist"], "goal_tags": ["general", "fatloss", "endurance"]},
    {"name": "Overhead Press", "pattern": "vertical_push", "equipment": ["barbell"], "level_min": "intermediate",
     "contra": ["shoulder_overhead", "wrist"], "goal_tags": ["strength", "hypertrophy"]},
    {"name": "Dumbbell Shoulder Press", "pattern": "vertical_push", "equipment": ["dumbbells"], "level_min": "beginner",
     "contra": ["shoulder_overhead", "wrist"], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Incline Dumbbell Press", "pattern": "push", "equipment": ["dumbbells"], "level_min": "beginner",
     "contra": ["wrist"], "goal_tags": ["hypertrophy", "general"]},

    # Pull
    {"name": "Pull-up", "pattern": "vertical_pull", "equipment": ["pullup_bar"], "level_min": "intermediate",
     "contra": [], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Chin-up", "pattern": "vertical_pull", "equipment": ["pullup_bar"], "level_min": "intermediate",
     "contra": [], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "One-arm Dumbbell Row", "pattern": "pull", "equipment": ["dumbbells"], "level_min": "beginner",
     "contra": ["lumbar_flexion", "wrist"], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Barbell Row", "pattern": "pull", "equipment": ["barbell"], "level_min": "intermediate",
     "contra": ["lumbar_flexion"], "goal_tags": ["strength", "hypertrophy"]},
    {"name": "Face Pull (Band)", "pattern": "pull", "equipment": ["bands"], "level_min": "beginner",
     "contra": [], "goal_tags": ["hypertrophy", "general"]},

    # Arms / Shoulders
    {"name": "Dumbbell Lateral Raise", "pattern": "push", "equipment": ["dumbbells"], "level_min": "beginner",
     "contra": ["shoulder_overhead"], "goal_tags": ["hypertrophy", "general"]},
    {"name": "Dumbbell Biceps Curl", "pattern": "pull", "equipment": ["dumbbells"], "level_min": "beginner",
     "contra": ["wrist"], "goal_tags": ["hypertrophy", "general"]},
    {"name": "Triceps Rope Pushdown (Band)", "pattern": "push", "equipment": ["bands"], "level_min": "beginner",
     "contra": ["wrist"], "goal_tags": ["hypertrophy", "general"]},

    # Core
    {"name": "Plank", "pattern": "core", "equipment": ["bodyweight"], "level_min": "beginner",
     "contra": [], "goal_tags": ["general", "fatloss", "endurance"]},
    {"name": "Side Plank", "pattern": "core", "equipment": ["bodyweight"], "level_min": "beginner",
     "contra": [], "goal_tags": ["general", "fatloss", "endurance"]},
    {"name": "Dead Bug", "pattern": "core", "equipment": ["bodyweight"], "level_min": "beginner",
     "contra": [], "goal_tags": ["general"]},
    {"name": "Hollow Body Hold", "pattern": "core", "equipment": ["bodyweight"], "level_min": "intermediate",
     "contra": [], "goal_tags": ["general"]},
    {"name": "Russian Twist", "pattern": "core", "equipment": ["bodyweight", "dumbbells"], "level_min": "beginner",
     "contra": ["lumbar_flexion"], "goal_tags": ["general", "fatloss"]},

    # Carries / Conditioning
    {"name": "Farmer Carry", "pattern": "carry", "equipment": ["dumbbells", "kettlebell"], "level_min": "beginner",
     "contra": [], "goal_tags": ["general", "fatloss", "endurance"]},
    {"name": "Jump Rope", "pattern": "carry", "equipment": ["bodyweight"], "level_min": "beginner",
     "contra": ["impact"], "goal_tags": ["fatloss", "endurance"]},

    # Mobility
    {"name": "World's Greatest Stretch", "pattern": "mobility", "equipment": ["bodyweight"], "level_min": "beginner",
     "contra": [], "goal_tags": ["mobility", "general"]},
    {"name": "90/90 Hip Switches", "pattern": "mobility", "equipment": ["bodyweight"], "level_min": "beginner",
     "contra": [], "goal_tags": ["mobility"]},
    {"name": "Cat-Cow", "pattern": "mobility", "equipment": ["bodyweight"], "level_min": "beginner",
     "contra": [], "goal_tags": ["mobility"]},
    {"name": "Thoracic Rotations", "pattern": "mobility", "equipment": ["bodyweight"], "level_min": "beginner",
     "contra": [], "goal_tags": ["mobility"]},
    {"name": "Ankle Dorsiflexion Mobilization", "pattern": "mobility", "equipment": ["bodyweight"], "level_min": "beginner",
     "contra": [], "goal_tags": ["mobility"]},
]

LEVEL_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}

# ================================
# Sidebar Inputs
# ================================
with st.sidebar:
    st.markdown("### Your Setup")
    st.caption("Tell us about your training. We’ll build the plan.")

    goal = st.selectbox(
        "Primary goal",
        ["Build Muscle (Hypertrophy)", "Get Stronger (Strength)", "Fat Loss / Conditioning", "General Fitness / Health", "Mobility / Flexibility"],
        index=0
    )
    days = st.slider("Days per week", 1, 6, 3)
    minutes = st.slider("Minutes per session", 20, 90, 45, 5)
    experience = st.selectbox("Training experience", ["Beginner", "Intermediate", "Advanced"], index=0)
    equip = st.multiselect(
        "Available equipment",
        ["Bodyweight", "Dumbbells", "Barbell", "Kettlebell", "Resistance Bands", "Pull-up Bar", "Machines"],
        default=["Bodyweight", "Dumbbells"]
    )
    constraints = st.multiselect(
        "Any limitations? (optional)",
        ["No deep knee flexion", "No overhead pressing", "No spinal flexion", "Avoid high impact", "Wrist pain", "Shoulder sensitive", "Lower back sensitive"],
        default=[]
    )
    focus = st.multiselect(
        "Emphasis (optional)",
        ["Full Body", "Upper Body", "Lower Body", "Glutes", "Core", "Arms", "Shoulders", "Back", "Chest"],
        default=["Full Body"]
    )
    seed = st.number_input(
        "Plan Code",
        min_value=0, max_value=10_000, value=42, step=1,
        help="Enter this code to recreate a previous plan. Leave as-is for a new plan."
    )

    # --- YouTube key + toggle + cache refresh ---
    YT_KEY = st.secrets.get("YT_API_KEY")
    has_key = bool(YT_KEY)
    include_videos = st.toggle("Show demo videos", value=False) if has_key else False
    if st.button("🔁 Refresh videos cache"):
        st.cache_data.clear()
        st.success("Cleared cached video lookups.")

    st.markdown("---")
    generate = st.button("🚀 Generate my plan", type="primary")

# ================================
# Helpers
# ================================
def _norm_equip(e: List[str]) -> List[str]:
    m = {
        "Bodyweight": "bodyweight", "Dumbbells": "dumbbells", "Barbell": "barbell",
        "Kettlebell": "kettlebell", "Resistance Bands": "bands", "Pull-up Bar": "pullup_bar", "Machines": "machines"
    }
    return [m[x] for x in e]

def _contra_from_constraints(c: List[str]) -> List[str]:
    mapping = {
        "No deep knee flexion": "knee",
        "No overhead pressing": "shoulder_overhead",
        "No spinal flexion": "lumbar_flexion",
        "Avoid high impact": "impact",
        "Wrist pain": "wrist",
        "Shoulder sensitive": "shoulder_overhead",
        "Lower back sensitive": "lumbar_flexion"
    }
    return list({mapping[x] for x in c})

def filter_exercises(goal_key: str, equip_norm: List[str], min_level: str, avoid: List[str]) -> List[Dict]:
    """Fix: Enforce level/equipment/contra + goal intent (except allow 'general'/'mobility' always)."""
    level_min = LEVEL_ORDER[min_level]
    out = []
    for ex in EXERCISES:
        if LEVEL_ORDER[ex["level_min"]] > level_min:
            continue
        if not any(e in equip_norm for e in ex["equipment"]):
            continue
        if any(a in ex["contra"] for a in avoid):
            continue
        if goal_key not in ["general", "mobility"] and goal_key not in ex["goal_tags"]:
            continue
        out.append(ex)
    return out

def difficulty_weight(ex: Dict, experience: str) -> int:
    """Weight exercises by appropriateness for the user's level."""
    w = 1
    lvl = LEVEL_ORDER[ex["level_min"]]
    if experience == "Beginner":
        w += 2 if lvl == 0 else 0
        w -= 1 if lvl >= 1 else 0
    elif experience == "Intermediate":
        w += 1 if lvl == 1 else 0
    else:  # Advanced
        w += 2 if lvl >= 1 else 0
        if "barbell" in ex["equipment"] and ex["pattern"] in ["squat", "hinge", "push", "pull", "vertical_push", "vertical_pull"]:
            w += 1
    return max(1, w)

def emphasize(exs: List[Dict], focus: List[str], experience: str) -> List[Dict]:
    """Compose difficulty weighting with user emphasis."""
    weighted = []
    for e in exs:
        w = difficulty_weight(e, experience)
        if "Lower Body" in focus and e["pattern"] in ["squat", "hinge", "lunge"]:
            w += 1
        if "Upper Body" in focus and e["pattern"] in ["push", "vertical_push", "pull", "vertical_pull"]:
            w += 1
        if "Core" in focus and e["pattern"] == "core":
            w += 1
        if "Glutes" in focus and e["pattern"] in ["hinge", "lunge", "squat"]:
            w += 1
        if "Arms" in focus and (e["name"].lower().endswith("curl") or "tricep" in e["name"].lower()):
            w += 1
        if "Shoulders" in focus and (e["pattern"] in ["vertical_push", "push"] or "lateral raise" in e["name"].lower()):
            w += 1
        if "Back" in focus and e["pattern"] in ["pull", "vertical_pull"]:
            w += 1
        if "Chest" in focus and e["pattern"] == "push":
            w += 1
        weighted.extend([e] * max(1, w))
    return weighted

def patterns_for_week(days: int, goal_key: str) -> List[List[str]]:
    """Goal-aware daily pattern lists with deduping."""
    base_map = {
        1: [["squat", "hinge", "push", "pull", "core"]],
        2: [["squat", "push", "pull", "core"], ["hinge", "push", "pull", "core"]],
        3: [["squat", "push", "pull", "core"], ["hinge", "push", "pull", "core"], ["lunge", "push", "pull", "core"]],
        4: [["upper"], ["lower"], ["upper"], ["lower"]],
        5: [["upper"], ["lower"], ["push"], ["pull"], ["legs"]],
        6: [["push"], ["pull"], ["legs"], ["upper"], ["lower"], ["core"]],
    }
    base = base_map[days][:]

    expanded = []
    for day in base:
        day_patterns = []
        for p in day:
            if p == "upper":
                day_patterns += ["push", "pull", "vertical_push", "vertical_pull", "core"]
            elif p == "lower":
                day_patterns += ["squat", "hinge", "lunge", "core"]
            elif p == "legs":
                day_patterns += ["squat", "hinge", "lunge"]
            elif p == "core":
                day_patterns += ["core", "carry"]
            else:
                day_patterns.append(p)

        # goal bias
        if goal_key == "strength":
            day_patterns += ["carry"]  # bracing
        elif goal_key == "hypertrophy":
            day_patterns += ["push", "pull"]  # extra pump
        elif goal_key in ["fatloss", "endurance"]:
            day_patterns += ["carry", "core"]  # circuit-friendly
        elif goal_key == "mobility":
            day_patterns = ["mobility", "core", "hinge", "squat"]

        uniq = []
        for x in day_patterns:
            if x not in uniq:
                uniq.append(x)
        expanded.append(uniq)
    return expanded

def scheme_for(goal_key: str, pattern: str, experience: str, minutes: int) -> Dict:
    """Different schemes by goal + level with Tempo & RIR."""
    notes = ""
    tempo = "2-0-2"
    rir = 2
    rest = 75
    sets = 3
    reps = "8–10"

    if goal_key == "strength":
        if pattern in ["squat", "hinge", "push", "pull", "vertical_push", "vertical_pull"]:
            sets, reps, rest = 4, "3–5", 150
            tempo, rir = "2-1-1", 2
            notes = "Power focus, crisp technique."
        else:
            sets, reps, rest = 3, "5–6", 120
            tempo, rir = "2-1-1", 1
    elif goal_key == "hypertrophy":
        sets, reps, rest = 3, "8–12", 75
        tempo, rir = "3-1-2", 1
        notes = "Challenging last reps, full range."
    elif goal_key in ["fatloss", "endurance"]:
        return {
            "type": "timed", "time_sec": 40, "rest_sec": 20, "sets": 3, "reps": None,
            "tempo": "constant", "rir": None,
            "notes": "Circuit pace; keep moving between exercises."
        }
    elif goal_key == "mobility":
        return {
            "type": "hold", "time_sec": 45, "rest_sec": 15, "sets": 2, "reps": None,
            "tempo": "slow", "rir": None,
            "notes": "Controlled range, breathe into end positions."
        }
    else:  # general
        sets, reps, rest = 3, "6–10", 90
        tempo, rir = "2-1-2", 2
        notes = "Smooth reps, own the range."

    # Level-based adjustments
    if experience == "Beginner":
        sets = max(2, sets - 1)
        rest = max(60, rest - 15)
        if isinstance(reps, str) and "–" in reps:
            lo, hi = [int(x) for x in reps.split("–")]
            reps = f"{lo+1}–{hi+2}"
        tempo = "2-0-2"
        rir = 2
        notes = (notes + " Leave 2–3 reps in reserve.").strip()
    elif experience == "Advanced":
        sets += 1
        rest += 15
        if isinstance(reps, str) and "–" in reps:
            lo, hi = [int(x) for x in reps.split("–")]
            reps = f"{max(3, lo-1)}–{max(lo, hi-1)}"
        tempo = "3-1-1" if goal_key in ["hypertrophy", "general"] else "2-1-1"
        rir = 1
        notes = (notes + " Optionally add a final hard set.").strip()

    # Time-pressure adjustment
    if minutes < 35:
        sets = max(2, sets - 1)
    elif minutes > 60:
        sets += 1

    return {
        "type": "sets_reps",
        "sets": sets,
        "reps": reps,
        "time_sec": None,
        "rest_sec": rest,
        "tempo": tempo,
        "rir": rir,
        "notes": notes
    }

def _avg_reps(reps_field) -> int:
    if isinstance(reps_field, int):
        return reps_field
    if isinstance(reps_field, str) and "–" in reps_field:
        lo, hi = [int(x) for x in reps_field.split("–")]
        return (lo + hi) // 2
    return 10

def estimate_exercise_time_sec(item: Dict) -> int:
    """Estimate work + rest + overhead per exercise (more realistic)."""
    if item["type"] == "timed":
        return (item["time_sec"] + item["rest_sec"]) * item["sets"] + 45
    if item["type"] == "hold":
        return (item["time_sec"] + item["rest_sec"]) * item["sets"] + 45

    reps = _avg_reps(item["reps"])
    try:
        ecc, pause, con = [int(x) for x in str(item.get("tempo", "2-0-2")).split("-")]
    except Exception:
        ecc, pause, con = 2, 0, 2

    time_per_rep = ecc + pause + con
    per_set_overhead = 12
    transition_between_exercises = 45

    work = (reps * time_per_rep + per_set_overhead) * item["sets"]
    rest_total = max(0, item["sets"] - 1) * item.get("rest_sec", 75)

    return work + rest_total + transition_between_exercises

@st.cache_data(show_spinner=False)
def get_youtube_id(query: str, api_key: Optional[str]) -> Optional[str]:
    """Return a YouTube videoId or None. Cached per (query, api_key)."""
    if not api_key:
        return None
    try:
        from googleapiclient.discovery import build
    except ModuleNotFoundError:
        st.info("YouTube client not installed on this deploy (check requirements.txt).")
        return None
    try:
        yt = build("youtube", "v3", developerKey=api_key)
        req = yt.search().list(
            q=query, part="id", type="video", maxResults=1, videoEmbeddable="true"
        )
        res = req.execute()
        items = res.get("items", [])
        if items:
            return items[0]["id"]["videoId"]
    except Exception:
        st.info("Couldn't fetch YouTube video automatically. You can still use the search links.")
    return None

def pick_for_pattern(candidates: List[Dict], pattern: str, used: set, rng: random.Random) -> Optional[Dict]:
    pool = [e for e in candidates if e["pattern"] == pattern and e["name"] not in used]
    if not pool:
        pool = [e for e in candidates if e["name"] not in used]
    if not pool:
        return None
    choice = rng.choice(pool)
    used.add(choice["name"])
    return choice

def build_day_plan(candidates: List[Dict], patterns: List[str], rng: random.Random,
                   goal_key: str, experience: str, minutes: int):
    """Time-aware builder with per-level min/max exercise caps (warm-up not counted)."""
    used = set()
    day_exercises = []
    time_budget = minutes * 60
    time_used = 0

    caps = {
        "Beginner":      {"min": 4, "max": 6},
        "Intermediate":  {"min": 5, "max": 7},
        "Advanced":      {"min": 5, "max": 8},
    }
    cap = caps.get(experience, {"min": 5, "max": 7})

    def count_main(exs):
        return sum(1 for x in exs if x.get("name") != "Warm-up")

    # Warm-up block (~5 min)
    warmup = {
        "name": "Warm-up",
        "pattern": "mobility",
        "type": "hold",
        "time_sec": 30,
        "rest_sec": 15,
        "sets": 6,
        "tempo": "easy",
        "rir": None,
        "notes": "3–5 min: light cardio + dynamic mobility (hips, T-spine, shoulders). Add 2 ramp sets for your first big lift."
    }
    time_used += estimate_exercise_time_sec(warmup)
    day_exercises.append(warmup)

    # Cover core patterns first
    for p in patterns:
        if count_main(day_exercises) >= cap["max"]:
            break
        ex = pick_for_pattern(candidates, p, used, rng)
        if not ex:
            continue
        scheme = scheme_for(goal_key, ex["pattern"], experience, minutes)
        item = {**ex, **scheme}
        t = estimate_exercise_time_sec(item)

        must_have = (goal_key in ["strength", "hypertrophy", "general"]) and \
                    (sum(1 for x in day_exercises if x.get("type") == "sets_reps") < 3)

        if must_have or time_used + t <= time_budget:
            day_exercises.append(item)
            time_used += t
        if count_main(day_exercises) >= cap["max"]:
            break

    # Fill remaining time up to caps
    tries = 0
    while time_used <= time_budget and tries < 30 and count_main(day_exercises) < cap["max"]:
        ex = pick_for_pattern(candidates, rng.choice(patterns), used, rng)
        if not ex:
            break
        item = {**ex, **scheme_for(goal_key, ex["pattern"], experience, minutes)}
        t = estimate_exercise_time_sec(item)
        if time_used + t > time_budget:
            break
        day_exercises.append(item)
        time_used += t
        tries += 1

    # Ensure minimum count if possible
    tries = 0
    while count_main(day_exercises) < cap["min"] and tries < 10:
        ex = pick_for_pattern(candidates, rng.choice(patterns), used, rng)
        if not ex:
            break
        item = {**ex, **scheme_for(goal_key, ex["pattern"], experience, minutes)}
        t = estimate_exercise_time_sec(item)
        if time_used + t > time_budget and count_main(day_exercises) >= (cap["min"] - 1):
            day_exercises.append(item)
            break
        if time_used + t <= time_budget:
            day_exercises.append(item)
            time_used += t
        tries += 1

    return day_exercises

def goal_key_from_label(lbl: str) -> str:
    m = {
        "Build Muscle (Hypertrophy)": "hypertrophy",
        "Get Stronger (Strength)": "strength",
        "Fat Loss / Conditioning": "fatloss",
        "General Fitness / Health": "general",
        "Mobility / Flexibility": "mobility",
    }
    return m[lbl]

def plan_to_dataframe(week_plan: Dict[int, List[Dict]], include_video_urls: bool) -> pd.DataFrame:
    rows = []
    for day_idx, items in week_plan.items():
        day_name = f"Day {day_idx+1}"
        for it in items:
            if it["type"] == "sets_reps":
                scheme = f'{it["sets"]} x {it["reps"]}'
                rest = it["rest_sec"]
            elif it["type"] == "timed":
                scheme = f'{it["sets"]} rounds of {it["time_sec"]}s work / {it["rest_sec"]}s rest'
                rest = it["rest_sec"]
            else:
                scheme = f'{it["sets"]} x {it["time_sec"]}s'
                rest = it["rest_sec"]
            video = ""
            if include_video_urls and it["name"] != "Warm-up":
                vid = get_youtube_id(f"{it['name']} exercise proper form tutorial", YT_KEY)
                if vid:
                    video = f"https://www.youtube.com/watch?v={vid}"
            rows.append({
                "Day": day_name,
                "Exercise": it["name"],
                "Pattern": it["pattern"],
                "Scheme": scheme,
                "Rest (s)": rest,
                "Tempo": it.get("tempo", ""),
                "RIR": it.get("rir", ""),
                "Notes": it.get("notes", ""),
                "Video": video
            })
    return pd.DataFrame(rows)

def markdown_plan(week_plan: Dict[int, List[Dict]], include_videos: bool) -> str:
    lines = ["# Weekly Workout Plan"]
    for day_idx, items in week_plan.items():
        lines.append(f"\n## Day {day_idx+1}\n")
        for it in items:
            if it["type"] == "sets_reps":
                scheme = f'{it["sets"]} x {it["reps"]} — rest {it["rest_sec"]}s'
            elif it["type"] == "timed":
                scheme = f'{it["sets"]} rounds — {it["time_sec"]}s work / {it["rest_sec"]}s rest'
            else:
                scheme = f'{it["sets"]} x {it["time_sec"]}s — rest {it["rest_sec"]}s'
            vid = ""
            if include_videos and it["name"] != "Warm-up":
                v = get_youtube_id(f"{it['name']} exercise proper form tutorial", YT_KEY)
                if v:
                    vid = f"  \n[Demo](https://www.youtube.com/watch?v={v})"
            extras = []
            if it.get("tempo"): extras.append(f"Tempo {it['tempo']}")
            if it.get("rir") is not None: extras.append(f"RIR {it['rir']}")
            extras_txt = (" — " + " · ".join(extras)) if extras else ""
            lines.append(f"- **{it['name']}** ({it['pattern']}) — {scheme}.{extras_txt} {it.get('notes','')}{vid}")
    return "\n".join(lines)

def summarize_day(day_items: List[Dict]) -> Dict:
    total_sets = sum(x["sets"] for x in day_items if x["type"] == "sets_reps")
    est_time = sum(estimate_exercise_time_sec(x) for x in day_items)
    patterns = [x["pattern"] for x in day_items if x.get("pattern")]
    return {"total_sets": total_sets, "est_min": round(est_time/60), "patterns": ", ".join(sorted(set(patterns)))}

# ================================
# UI Flow
# ================================
if 'generated_once' not in st.session_state:
    st.info("Use the panel on the left to set your goal and schedule, then hit **Generate my plan**.")

if generate:
    st.session_state.generated_once = True
    rng = random.Random(seed)
    goal_key = goal_key_from_label(goal)
    equip_norm = _norm_equip(equip)
    avoid = _contra_from_constraints(constraints)
    min_level = experience.lower()

    candidates = filter_exercises(goal_key, equip_norm, min_level, avoid)
    if not candidates:
        st.error("No exercises matched your filters. Try adding more equipment or removing limitations.")
        st.stop()

    patterns_week = patterns_for_week(days, goal_key)
    week_plan: Dict[int, List[Dict]] = {}

    # Build per-day with deterministic RNG based on (seed, day_index)
    for i, patterns in enumerate(patterns_week):
        day_rng = random.Random(seed * 1000 + i)
        cand_weighted = emphasize(candidates, focus, experience)
        day = build_day_plan(cand_weighted, patterns, day_rng, goal_key, experience, minutes)
        week_plan[i] = day

    st.success("Plan generated! Scroll down to view your week.")

    tabs = st.tabs([f"Day {i+1}" for i in range(days)] + ["Download / Export"])

    # Day tabs
    for i in range(days):
        with tabs[i]:
            st.subheader(f"Day {i+1}")

            day_items = week_plan[i]
            summary = summarize_day(day_items)
            st.caption(f"**Summary:** {summary['total_sets']} total sets · ~{summary['est_min']} min · Patterns: {summary['patterns']}")

            for j, it in enumerate(day_items, start=1):
                header = f"{j}. {it['name']} · <small>{it['pattern']}</small>"
                if it["type"] == "sets_reps":
                    scheme_txt = f"{it['sets']} × {it['reps']} · Rest {it['rest_sec']}s"
                elif it["type"] == "timed":
                    scheme_txt = f"Circuit: {it['sets']} rounds — {it['time_sec']}s work / {it['rest_sec']}s rest"
                else:
                    scheme_txt = f"Holds: {it['sets']} × {it['time_sec']}s · Rest {it['rest_sec']}s"

                tempo = it.get("tempo")
                rir = it.get("rir")
                extra = []
                if tempo: extra.append(f"Tempo {tempo}")
                if rir is not None: extra.append(f"RIR {rir}")
                extras = " · ".join(extra)

                st.markdown(f'''
<div class="card">
  <h4>{header}</h4>
  <div>{scheme_txt}{(" · " + extras) if extras else ""}</div>
  <small>{it.get('notes','')}</small>
</div>
''', unsafe_allow_html=True)

                # Video + search link (limit auto-fetch to first 3 non-warm-up exercises)
                if include_videos and it["name"] != "Warm-up" and j <= 3:
                    vid = get_youtube_id(f"{it['name']} exercise proper form tutorial", YT_KEY)
                    if vid:
                        with st.expander("Watch demo"):
                            st.video(f"https://www.youtube.com/watch?v={vid}")

                if it["name"] != "Warm-up":
                    search_q = it["name"].replace(" ", "+") + "+exercise+proper+form+tutorial"
                    st.markdown(f"[Search on YouTube for demo](https://www.youtube.com/results?search_query={search_q})")

    # Export tab
    with tabs[-1]:
        df = plan_to_dataframe(week_plan, include_videos)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download as CSV", data=csv, file_name="workout_plan.csv", mime="text/csv")

        md = markdown_plan(week_plan, include_videos).encode("utf-8")
        st.download_button("⬇️ Download as Markdown", data=md, file_name="workout_plan.md", mime="text/markdown")
