import streamlit as st
import requests
import random
from collections import Counter

# -----------------------------
# 💅 Aesthetic Mobile-Friendly CSS Injection
# -----------------------------
st.markdown(
    """
    <style>
    /* Background image styling */
    body {
        background: url('https://raw.githubusercontent.com/karenrenac/roster-app/main/download.jpg'), 
                    url('https://raw.githubusercontent.com/karenrenac/roster-app/main/download.jpg');
        background-repeat: repeat-y, repeat-y;
        background-position: left center, right center;
        background-size: contain, contain;
        background-attachment: fixed, fixed;
        background-color: #0e1117;
    }

    /* Center content block */
    .block-container {
        background-color: rgba(0, 0, 0, 0.85);
        max-width: 900px;
        margin: auto;
        padding: 2rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0px 0px 25px rgba(0,0,0,0.6);
    }

    /* Mobile tweaks */
    @media only screen and (max-width: 768px) {
        body {
            background-position: center top;
            background-size: cover;
        }
        .block-container {
            padding: 1rem;
            max-width: 95%;
        }
        h1, h2, h3 {
            font-size: 1.5rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 🔐 Supabase Setup
# -----------------------------
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# -----------------------------
# 🔁 Supabase Functions
# -----------------------------
def load_friends():
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/Friends?select=*", headers=HEADERS)
        data = res.json()
        return [f["name"] for f in data if "name" in f]
    except Exception as e:
        st.error(f"❌ Failed to load friends: {e}")
        return []

def add_friend(name):
    try:
        payload = {"name": name}
        headers = {**HEADERS, "Prefer": "return=representation"}
        res = requests.post(f"{SUPABASE_URL}/rest/v1/Friends", headers=headers, json=payload)
        if res.status_code == 409:
            st.warning(f"⚠️ '{name}' already exists.")
        elif res.status_code in [200, 201]:
            st.success(f"✅ {name} added!")
        else:
            st.error(f"❌ Failed: {res.text}")
    except Exception as e:
        st.error(f"❌ Error adding friend: {e}")

def delete_friend(name):
    try:
        res = requests.delete(f"{SUPABASE_URL}/rest/v1/Friends?name=eq.{name}", headers=HEADERS)
        return res.status_code == 204
    except:
        return False

def load_history():
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/History?select=id,person1,person2", headers=HEADERS)
        data = res.json()
        return [(h["id"], h["person1"], h["person2"]) for h in data]
    except Exception as e:
        st.error(f"❌ Failed to load history: {e}")
        return []

def add_history(p1, p2):
    try:
        payload = {"person1": p1, "person2": p2}
        headers = {**HEADERS, "Prefer": "return=representation"}
        res = requests.post(f"{SUPABASE_URL}/rest/v1/History", headers=headers, json=payload)
        if res.status_code in [200, 201]:
            record = res.json()[0]
            st.session_state.history.append((record["id"], record["person1"], record["person2"]))
            st.success(f"✅ {p1} & {p2} picked!")
    except Exception as e:
        st.error(f"❌ Error adding history: {e}")

def delete_last_trip():
    if st.session_state.history:
        last_id, p1, p2 = st.session_state.history[-1]
        try:
            res = requests.delete(f"{SUPABASE_URL}/rest/v1/History?id=eq.{last_id}", headers=HEADERS)
            if res.status_code == 204:
                st.session_state.history.pop()
                st.success(f"🗑️ Removed trip: {p1} & {p2}")
        except Exception as e:
            st.error(f"❌ Error deleting last trip: {e}")

# -----------------------------
# 🔄 Init Session State
# -----------------------------
if 'friends' not in st.session_state:
    st.session_state.friends = load_friends()
if 'history' not in st.session_state:
    st.session_state.history = load_history()
if 'present_friends' not in st.session_state:
    st.session_state.present_friends = []
if 'excluded_friends' not in st.session_state:
    st.session_state.excluded_friends = []

# -----------------------------
# 🎯 UI Starts
# -----------------------------
st.markdown("# 🥤 NOT IT! – Who's Going to the Store?")

# ➕ Add Friend
st.markdown("### ➕ Add a Friend")
new_friend = st.text_input("Add a new friend:")
if st.button("Add Friend"):
    if not new_friend.strip():
        st.warning("Enter a valid name.")
    elif new_friend in st.session_state.friends:
        st.info("Already exists.")
    else:
        add_friend(new_friend.strip())
        st.session_state.friends = load_friends()

# 👥 Show All Friends
st.markdown("### 🧑‍🤝‍🧑 All Friends")
st.write(st.session_state.friends)

# 🗑️ Delete Friend
st.markdown("### 🗑️ Remove a Friend")
if st.session_state.friends:
    friend_to_delete = st.selectbox("Select friend to delete:", st.session_state.friends)
    if st.button("Delete Friend"):
        if delete_friend(friend_to_delete):
            st.session_state.friends = load_friends()
            st.session_state.present_friends = [f for f in st.session_state.present_friends if f != friend_to_delete]
            st.session_state.excluded_friends = [f for f in st.session_state.excluded_friends if f != friend_to_delete]
            st.success(f"{friend_to_delete} deleted.")

# ✅ Present Today
st.markdown("### ✅ Who's Present Today?")
st.session_state.present_friends = st.multiselect("Select who's around today:", st.session_state.friends, default=st.session_state.present_friends)

# 🙅‍♂️ Exclude Friends
st.markdown("### 🙅‍♂️ Exclude Friends")
st.session_state.excluded_friends = st.multiselect("Exclude from pick:", st.session_state.present_friends, default=st.session_state.excluded_friends)

# 🎲 Pick Two
st.markdown("### 🎲 Pick Who's Going!")
if st.button("Pick Next Two"):
    available = list(set(st.session_state.present_friends) - set(st.session_state.excluded_friends))
    if len(available) < 2:
        st.warning("Need at least 2 friends to pick from.")
    else:
        recent = st.session_state.history[-3:]
        recent_people = {p for _, p1, p2 in recent for p in (p1, p2)}
        pool = list(set(available) - recent_people)
        if len(pool) < 2:
            st.session_state.history = []
            pool = available
            st.info("Resetting history.")
        chosen = random.sample(pool, 2)
        add_history(chosen[0], chosen[1])

# 🔁 Undo Last
if st.button("Undo Last Trip"):
    delete_last_trip()

# 📈 Stats
st.markdown("### 📊 Store Visit Stats")
if st.session_state.history:
    all_people = [p for _, p1, p2 in st.session_state.history for p in (p1, p2)]
    counts = Counter(all_people)
    for f in st.session_state.friends:
        st.write(f"**{f}** → {counts.get(f, 0)} trips")
else:
    st.write("No visits yet.")

# 📜 Past Trips
st.markdown("### 🕓 Past Store Trips")
if st.session_state.history:
    for i, (_, p1, p2) in enumerate(reversed(st.session_state.history), 1):
        st.write(f"{i}. {p1} & {p2}")
else:
    st.write("No history yet.")
