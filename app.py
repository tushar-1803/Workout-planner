import random
from typing import List, Dict, Optional, Tuple
import streamlit as st
import pandas as pd
import numpy as np
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from typing import List, Dict, Optional

# Try importing sklearn. If missing (e.g., before requirements install),
# we'll fall back to a deterministic, simple selector.
_SKLEARN_OK = True
try:
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    _SKLEARN_OK = False


# -----------------------------------------------------------------------------
# App Config & Global Styles
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Custom Workout Planner (ML)", page_icon="💪", layout="wide")

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
/* cards */
.card {border-radius:16px; padding:14px 16px; background:#1C2541; border:1px solid rgba(255,255,255,.06); margin-bottom:10px;}
.card h4{margin:0 0 .25rem 0; font-size:1rem;}
.card small{color:#9FB0C3;}
/* nicer buttons */
.stDownloadButton button, .stButton button {border-radius:999px; padding:.6rem 1rem; font-weight:700;}
/* sidebar spacing */
[data-testid="stSidebar"] .block-container {padding-top: 1rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">Custom Workout Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Now powered by a lightweight ML recommender — it ranks exercises to match your goal, time, experience & equipment, then builds your week with smart variety.</div>', unsafe_allow_html=True)
st.markdown('<span class="badge">💪 Strength</span><span class="badge">🌟 Hypertrophy</span><span class="badge">🔥 Conditioning</span><span class="badge">🧘 Mobility</span>', unsafe_allow_html=True)
st.write("")


# -----------------------------------------------------------------------------
# Exercise Library (metadata the model learns from)
# -----------------------------------------------------------------------------
# pattern: 'squat' | 'hinge' | 'lunge' | 'push' | 'vertical_push' | 'pull' | 'vertical_pull' | 'core' | 'carry' | 'mobility'
# equipment: 'bodyweight', 'dumbbells', 'barbell', 'kettlebell', 'bands', 'pullup_bar', 'machines'
# contraindications: 'knee', 'shoulder_overhead', 'lumbar_flexion', 'wrist', 'impact'
EXERCISES: List[Dict] = [
    # Lower body
    {"name": "Back Squat", "pattern": "squat", "equipment": ["barbell"], "level_min": "intermediate", "contra": ["knee"], "goal_tags": ["strength", "hypertrophy"]},
    {"name": "Goblet Squat", "pattern": "squat", "equipment": ["dumbbells"], "level_min": "beginner", "contra": ["knee"], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Bodyweight Squat", "pattern": "squat", "equipment": ["bodyweight"], "level_min": "beginner", "contra": ["knee"], "goal_tags": ["general", "fatloss", "endurance"]},
    {"name": "Romanian Deadlift", "pattern": "hinge", "equipment": ["barbell", "dumbbells"], "level_min": "beginner", "contra": ["lumbar_flexion"], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Conventional Deadlift", "pattern": "hinge", "equipment": ["barbell"], "level_min": "intermediate", "contra": ["lumbar_flexion"], "goal_tags": ["strength", "hypertrophy"]},
    {"name": "Hip Thrust", "pattern": "hinge", "equipment": ["barbell", "dumbbells"], "level_min": "beginner", "contra": [], "goal_tags": ["hypertrophy", "general"]},
    {"name": "Kettlebell Swing", "pattern": "hinge", "equipment": ["kettlebell"], "level_min": "beginner", "contra": ["lumbar_flexion", "impact"], "goal_tags": ["fatloss", "endurance", "general"]},
    {"name": "Walking Lunge", "pattern": "lunge", "equipment": ["bodyweight", "dumbbells"], "level_min": "beginner", "contra": ["knee", "impact"], "goal_tags": ["hypertrophy", "general", "fatloss"]},
    {"name": "Bulgarian Split Squat", "pattern": "lunge", "equipment": ["bodyweight", "dumbbells"], "level_min": "intermediate", "contra": ["knee"], "goal_tags": ["hypertrophy", "general"]},
    {"name": "Step-up", "pattern": "lunge", "equipment": ["bodyweight", "dumbbells"], "level_min": "beginner", "contra": ["knee", "impact"], "goal_tags": ["general", "hypertrophy"]},

    # Push
    {"name": "Bench Press", "pattern": "push", "equipment": ["barbell"], "level_min": "intermediate", "contra": ["wrist"], "goal_tags": ["strength", "hypertrophy"]},
    {"name": "Dumbbell Bench Press", "pattern": "push", "equipment": ["dumbbells"], "level_min": "beginner", "contra": ["wrist"], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Push-up", "pattern": "push", "equipment": ["bodyweight"], "level_min": "beginner", "contra": ["wrist"], "goal_tags": ["general", "fatloss", "endurance"]},
    {"name": "Overhead Press", "pattern": "vertical_push", "equipment": ["barbell"], "level_min": "intermediate", "contra": ["shoulder_overhead", "wrist"], "goal_tags": ["strength", "hypertrophy"]},
    {"name": "Dumbbell Shoulder Press", "pattern": "vertical_push", "equipment": ["dumbbells"], "level_min": "beginner", "contra": ["shoulder_overhead", "wrist"], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Incline Dumbbell Press", "pattern": "push", "equipment": ["dumbbells"], "level_min": "beginner", "contra": ["wrist"], "goal_tags": ["hypertrophy", "general"]},

    # Pull
    {"name": "Pull-up", "pattern": "vertical_pull", "equipment": ["pullup_bar"], "level_min": "intermediate", "contra": [], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Chin-up", "pattern": "vertical_pull", "equipment": ["pullup_bar"], "level_min": "intermediate", "contra": [], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "One-arm Dumbbell Row", "pattern": "pull", "equipment": ["dumbbells"], "level_min": "beginner", "contra": ["lumbar_flexion", "wrist"], "goal_tags": ["strength", "hypertrophy", "general"]},
    {"name": "Barbell Row", "pattern": "pull", "equipment": ["barbell"], "level_min": "intermediate", "contra": ["lumbar_flexion"], "goal_tags": ["strength", "hypertrophy"]},
    {"name": "Face Pull (Band)", "pattern": "pull", "equipment": ["bands"], "level_min": "beginner", "contra": [], "goal_tags": ["hypertrophy", "general"]},

    # Arms / Shoulders
    {"name": "Dumbbell Lateral Raise", "pattern": "push", "equipment": ["dumbbells"], "level_min": "beginner", "contra": ["shoulder_overhead"], "goal_tags": ["hypertrophy", "general"]},
    {"name": "Dumbbell Biceps Curl", "pattern": "pull", "equipment": ["dumbbells"], "level_min": "beginner", "contra": ["wrist"], "goal_tags": ["hypertrophy", "general"]},
    {"name": "Triceps Rope Pushdown (Band)", "pattern": "push", "equipment": ["bands"], "level_min": "beginner", "contra": ["wrist"], "goal_tags": ["hypertrophy", "general"]},

    # Core
    {"name": "Plank", "pattern": "core", "equipment": ["bodyweight"], "level_min": "beginner", "contra": [], "goal_tags": ["general", "fatloss", "endurance"]},
    {"name": "Side Plank", "pattern": "core", "equipment": ["bodyweight"], "level_min": "beginner", "contra": [], "goal_tags": ["general", "fatloss", "endurance"]},
    {"name": "Dead Bug", "pattern": "core", "equipment": ["bodyweight"], "level_min": "beginner", "contra": [], "goal_tags": ["general"]},
    {"name": "Hollow Body Hold", "pattern": "core", "equipment": ["bodyweight"], "level_min": "intermediate", "contra": [], "goal_tags": ["general"]},
    {"name": "Russian Twist", "pattern": "core", "equipment": ["bodyweight", "dumbbells"], "level_min": "beginner", "contra": ["lumbar_flexion"], "goal_tags": ["general", "fatloss"]},

    # Carries / Conditioning
    {"name": "Farmer Carry", "pattern": "carry", "equipment": ["dumbbells", "kettlebell"], "level_min": "beginner", "contra": [], "goal_tags": ["general", "fatloss", "endurance"]},
    {"name": "Jump Rope", "pattern": "carry", "equipment": ["bodyweight"], "level_min": "beginner", "contra": ["impact"], "goal_tags": ["fatloss", "endurance"]},

    # Mobility
    {"name": "World's Greatest Stretch", "pattern": "mobility", "equipment": ["bodyweight"], "level_min": "beginner", "contra": [], "goal_tags": ["mobility", "general"]},
    {"name": "90/90 Hip Switches", "pattern": "mobility", "equipment": ["bodyweight"], "level_min": "beginner", "contra": [], "goal_tags": ["mobility"]},
    {"name": "Cat-Cow", "pattern": "mobility", "equipment": ["bodyweight"], "level_min": "beginner", "contra": [], "goal_tags": ["mobility"]},
    {"name": "Thoracic Rotations", "pattern": "mobility", "equipment": ["bodyweight"], "level_min": "beginner", "contra": [], "goal_tags": ["mobility"]},
    {"name": "Ankle Dorsiflexion Mobilization", "pattern": "mobility", "equipment": ["bodyweight"], "level_min": "beginner", "contra": [], "goal_tags": ["mobility"]},
]

LEVEL_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}


# -----------------------------------------------------------------------------
# Sidebar Inputs
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Your Setup")
    st.caption("Tell us about your training. We’ll build the plan.")
    goal_label = st.selectbox(
        "Primary goal",
        [
            "Build Muscle (Hypertrophy)",
            "Get Stronger (Strength)",
            "Fat Loss / Conditioning",
            "General Fitness / Health",
            "Mobility / Flexibility",
        ],
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
    seed = st.number_input("Plan Code", min_value=0, max_value=10_000, value=42, step=1,
                           help="Enter this code to recreate a previous plan. Leave as-is for a new plan.")

    if "YT_API_KEY" in st.secrets and st.secrets["YT_API_KEY"]:
        include_videos = st.toggle("Show demo videos", value=False)
    else:
        include_videos = False
        st.caption("YouTube embeds disabled (no API key in app secrets).")

    st.markdown("---")
    generate = st.button("🚀 Generate my plan", type="primary")


# -----------------------------------------------------------------------------
# Helpers: mapping & formatting
# -----------------------------------------------------------------------------
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

def goal_key_from_label(lbl: str) -> str:
    m = {
        "Build Muscle (Hypertrophy)": "hypertrophy",
        "Get Stronger (Strength)": "strength",
        "Fat Loss / Conditioning": "fatloss",
        "General Fitness / Health": "general",
        "Mobility / Flexibility": "mobility",
    }
    return m[lbl]

def scheme_for(goal_key: str, pattern: str, experience: str, minutes: int) -> Dict:
    """Same progression logic as before (sets/reps/rest), separate from selection engine."""
    sets = 3; reps = 10; rest = 60; notes = ""

    if goal_key == "strength":
        if pattern in ["squat", "hinge", "push", "pull", "vertical_push", "vertical_pull"]:
            sets, reps, rest = 4, 5, 120
            notes = "Heavy but crisp reps. Leave 1–2 reps in reserve."
        else:
            sets, reps, rest = 3, 6, 90
            notes = "Controlled tempo; prioritize quality."
    elif goal_key == "hypertrophy":
        sets, reps, rest = 3, 10, 75
        notes = "Last 2–3 reps challenging with good form."
    elif goal_key in ["fatloss", "endurance"]:
        return {"type": "timed", "time_sec": 40, "rest_sec": 20, "sets": 3, "reps": None,
                "notes": "Move briskly. Circuit style; repeat all exercises for 3 rounds."}
    elif goal_key == "mobility":
        return {"type": "hold", "time_sec": 45, "rest_sec": 15, "sets": 2, "reps": None,
                "notes": "Slow, controlled range. Breathe."}
    else:
        sets, reps, rest = 3, 8, 90
        notes = "Smooth reps, full range."

    if experience == "Beginner":
        sets = max(2, sets - 1); rest = max(60, rest - 15)
    elif experience == "Advanced":
        sets += 1; rest += 15

    if minutes < 35:
        sets = max(2, sets - 1)
    elif minutes > 60:
        sets += 1

    return {"type": "sets_reps", "sets": sets, "reps": reps, "time_sec": None, "rest_sec": rest, "notes": notes}


# -----------------------------------------------------------------------------
# ML Selection Engine
# -----------------------------------------------------------------------------
def _exercise_feature_dicts(exs: List[Dict]) -> List[Dict]:
    """Convert exercises to feature dicts for DictVectorizer."""
    rows = []
    for e in exs:
        row = {
            f"pattern={e['pattern']}": 1.0,
            f"level_min={e['level_min']}": 1.0,
        }
        for eq in e["equipment"]:
            row[f"equip={eq}"] = 1.0
        for g in e["goal_tags"]:
            row[f"goal={g}"] = 1.0
        for c in e["contra"]:
            row[f"contra={c}"] = 1.0
        rows.append(row)
    return rows

def _user_pref_features(goal_key: str, equip_norm: List[str], experience: str,
                        avoid: List[str], focus: List[str]) -> Dict:
    """Build a user preference feature dict."""
    f = {
        f"goal={goal_key}": 3.0,  # weight goal strongly
        f"level_min={experience.lower()}": 1.0,
    }
    # Available equipment positive signal
    for eq in equip_norm:
        f[f"equip={eq}"] = 1.5
    # Penalize contraindications (negative weight)
    for a in avoid:
        f[f"contra={a}"] = -2.0
    # Focus areas -> pattern priors
    focus_map = {
        "Lower Body": ["squat", "hinge", "lunge"],
        "Upper Body": ["push", "vertical_push", "pull", "vertical_pull"],
        "Core": ["core"],
        "Glutes": ["hinge", "lunge", "squat"],
        "Arms": ["push", "pull"],
        "Shoulders": ["vertical_push", "push"],
        "Back": ["pull", "vertical_pull"],
        "Chest": ["push"],
    }
    for tag in focus:
        for p in focus_map.get(tag, []):
            f[f"pattern={p}"] = f.get(f"pattern={p}", 0.0) + 0.8
    # Gentle general bias if user chose general/mobility
    if goal_key in ["general", "mobility"]:
        f["goal=general"] = f.get("goal=general", 0.0) + 0.5
    return f

def _pattern_distribution_for_goal(exs: List[Dict], goal_key: str) -> Dict[str, float]:
    """Learn a simple probability over patterns conditioned on goal (counts -> probs)."""
    counts = {}
    for e in exs:
        if goal_key in e["goal_tags"] or goal_key in ["general", "mobility"]:
            counts[e["pattern"]] = counts.get(e["pattern"], 0) + 1
    if not counts:
        return {p: 1.0 for p in ["push","pull","squat","hinge","lunge","core","vertical_push","vertical_pull","carry","mobility"]}
    total = sum(counts.values())
    # Normalize + smooth a little to never zero‑out categories
    return {k: (v / total) * 0.9 + 0.1/len(counts) for k, v in counts.items()}

def _target_exercises_per_session(minutes: int) -> int:
    if minutes < 35: return 4
    if minutes > 60: return 6
    return 5

def _rank_exercises(exs: List[Dict], user_vec: DictVectorizer, ex_matrix: np.ndarray, user_features: Dict) -> List[int]:
    """Return exercise indices sorted by similarity to user features."""
    u = user_vec.transform([user_features])
    sims = cosine_similarity(u, ex_matrix)[0]
    return list(np.argsort(-sims))  # descending

def _sample_week_plan_ml(
    exs: List[Dict],
    rank_order: List[int],
    goal_key: str,
    days: int,
    minutes: int,
    rng: random.Random
) -> Dict[int, List[Dict]]:
    """Sample a weekly plan from the ranked list using learned pattern distribution."""
    per_day = _target_exercises_per_session(minutes)
    # Learn pattern distribution for the chosen goal
    p_dist = _pattern_distribution_for_goal(exs, goal_key)
    # Create per-pattern ranked buckets to improve matching
    buckets: Dict[str, List[Dict]] = {}
    for idx in rank_order:
        e = exs[idx]
        buckets.setdefault(e["pattern"], []).append(e)

    plan: Dict[int, List[Dict]] = {}
    for d in range(days):
        day = []
        used_names = set()
        # Draw patterns by probability, but ensure diversity by avoiding duplicates first
        for _ in range(per_day * 2):  # allow retries
            if len(day) >= per_day:
                break
            # sample a pattern weighted by p_dist
            patterns, probs = zip(*p_dist.items())
            pattern = rng.choices(patterns, weights=probs, k=1)[0]
            pool = buckets.get(pattern, [])
            # pick the first ranked item not yet used
            pick = None
            for ex in pool:
                if ex["name"] not in used_names:
                    pick = ex
                    break
            if pick is None:
                # fall back: scan global ranked list for next unused
                for idx in rank_order:
                    ex = exs[idx]
                    if ex["name"] not in used_names:
                        pick = ex; break
            if pick:
                day.append(pick)
                used_names.add(pick["name"])
        # If still short, pad from global ranked list
        if len(day) < per_day:
            for idx in rank_order:
                if len(day) >= per_day:
                    break
                ex = exs[idx]
                if ex["name"] not in used_names:
                    day.append(ex)
                    used_names.add(ex["name"])
        plan[d] = day
    return plan


# -----------------------------------------------------------------------------
# YouTube helper (unchanged behavior)
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_youtube_id(query: str) -> Optional[str]:
    api_key = st.secrets.get("YT_API_KEY", None)
    if not api_key:
        return None
    try:
        from googleapiclient.discovery import build
        yt = build("youtube", "v3", developerKey=api_key)
        req = yt.search().list(q=query, part="id", type="video", maxResults=1, videoEmbeddable="true")
        res = req.execute()
        items = res.get("items", [])
        if items:
            return items[0]["id"]["videoId"]
    except Exception:
        # Silent failure: just skip embeds (link will still be shown)
        return None
    return None


# -----------------------------------------------------------------------------
# Export helpers
# -----------------------------------------------------------------------------
def plan_to_dataframe(week_plan: Dict[int, List[Dict]], include_video_urls: bool) -> pd.DataFrame:
    rows = []
    for day_idx, items in week_plan.items():
        day_name = f"Day {day_idx+1}"
        for it in items:
            sch = scheme_for(chosen_goal_key, it["pattern"], experience, minutes)
            if sch["type"] == "sets_reps":
                scheme = f'{sch["sets"]} x {sch["reps"]}'
                rest = sch["rest_sec"]
            elif sch["type"] == "timed":
                scheme = f'{sch["sets"]} rounds of {sch["time_sec"]}s work / {sch["rest_sec"]}s rest'
                rest = sch["rest_sec"]
            else:
                scheme = f'{sch["sets"]} x {sch["time_sec"]}s'
                rest = sch["rest_sec"]
            video = ""
            if include_video_urls:
                vid = get_youtube_id(f"{it['name']} exercise proper form tutorial")
                if vid:
                    video = f"https://www.youtube.com/watch?v={vid}"
            rows.append({
                "Day": day_name,
                "Exercise": it["name"],
                "Pattern": it["pattern"],
                "Scheme": scheme,
                "Rest (s)": rest,
                "Notes": sch.get("notes", ""),
                "Video": video
            })
    return pd.DataFrame(rows)

def markdown_plan(week_plan: Dict[int, List[Dict]], include_videos: bool) -> str:
    lines = ["# Weekly Workout Plan"]
    for day_idx, items in week_plan.items():
        lines.append(f"\n## Day {day_idx+1}\n")
        for it in items:
            sch = scheme_for(chosen_goal_key, it["pattern"], experience, minutes)
            if sch["type"] == "sets_reps":
                scheme = f'{sch["sets"]} x {sch["reps"]} — rest {sch["rest_sec"]}s'
            elif sch["type"] == "timed":
                scheme = f'{sch["sets"]} rounds — {sch["time_sec"]}s work / {sch["rest_sec"]}s rest'
            else:
                scheme = f'{sch["sets"]} x {sch["time_sec"]}s — rest {sch["rest_sec"]}s'
            vid = ""
            if include_videos:
                v = get_youtube_id(f"{it['name']} exercise proper form tutorial")
                if v:
                    vid = f"  \n[Demo](https://www.youtube.com/watch?v={v})"
            lines.append(f"- **{it['name']}** ({it['pattern']}) — {scheme}. {sch.get('notes','')}{vid}")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# UI Flow
# -----------------------------------------------------------------------------
if 'generated_once' not in st.session_state:
    st.info("Set your goal & schedule on the left, then hit **Generate my plan**.")

if generate:
    rng = random.Random(seed)
    chosen_goal_key = goal_key_from_label(goal_label)
    equip_norm = _norm_equip(equip)
    avoid = _contra_from_constraints(constraints)

    # --- Build ML vectors ---
    if _SKLEARN_OK:
        vec = DictVectorizer(sparse=True)
        X = vec.fit_transform(_exercise_feature_dicts(EXERCISES))
        ufeat = _user_pref_features(chosen_goal_key, equip_norm, experience, avoid, focus)
        ranked_idx = _rank_exercises(EXERCISES, vec, X, ufeat)
        week_plan = _sample_week_plan_ml(EXERCISES, ranked_idx, chosen_goal_key, days, minutes, rng)
    else:
        # Fallback: if sklearn not available yet (first run before requirements install)
        st.warning("scikit-learn not available yet. Using a simple selector until dependencies finish installing.")
        # naive ranking: filter by equipment/constraints/level, then order by goal tag presence
        lvl_min = LEVEL_ORDER[experience.lower()]
        pool = []
        for e in EXERCISES:
            if LEVEL_ORDER[e["level_min"]] > lvl_min:
                continue
            if not any(eq in equip_norm for eq in e["equipment"]):
                continue
            if any(a in e["contra"] for a in avoid):
                continue
            score = 1 if chosen_goal_key in e["goal_tags"] else 0
            pool.append((score, e))
        pool.sort(key=lambda x: (-x[0], x[1]["name"]))
        ranked_exs = [e for _, e in pool] + [e for e in EXERCISES if e not in [x[1] for x in pool]]
        # simple bucket plan
        per_day = _target_exercises_per_session(minutes)
        week_plan = {}
        idx = 0
        for d in range(days):
            day = []
            used = set()
            while len(day) < per_day and idx < len(ranked_exs):
                ex = ranked_exs[idx]; idx += 1
                if ex["name"] in used: continue
                used.add(ex["name"]); day.append(ex)
            week_plan[d] = day

    st.success("Plan generated! Scroll down to view your week.")
    tabs = st.tabs([f"Day {i+1}" for i in range(days)] + ["Download / Export"])

    # Render daily tabs
    for i in range(days):
        with tabs[i]:
            st.subheader(f"Day {i+1}")
            day_items = week_plan[i]
            for j, it in enumerate(day_items, start=1):
                sch = scheme_for(chosen_goal_key, it["pattern"], experience, minutes)
                header = f"{j}. {it['name']} · <small>{it['pattern']}</small>"
                if sch["type"] == "sets_reps":
                    scheme_txt = f"{sch['sets']} × {sch['reps']} · Rest {sch['rest_sec']}s"
                elif sch["type"] == "timed":
                    scheme_txt = f"Circuit: {sch['sets']} rounds — {sch['time_sec']}s work / {sch['rest_sec']}s rest"
                else:
                    scheme_txt = f"Holds: {sch['sets']} × {sch['time_sec']}s · Rest {sch['rest_sec']}s"

                st.markdown(f'''
<div class="card">
  <h4>{header}</h4>
  <div>{scheme_txt}</div>
  <small>{sch.get('notes','')}</small>
</div>
''', unsafe_allow_html=True)

                # Video embed or search link
                if include_videos:
                    vid = get_youtube_id(f"{it['name']} exercise proper form tutorial")
                    if vid:
                        with st.expander("Watch demo"):
                            st.video(f"https://www.youtube.com/watch?v={vid}")
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
