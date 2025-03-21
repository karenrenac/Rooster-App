import streamlit as st
import requests
import random
from collections import Counter

# ------------------------------
# 🔐 Supabase Setup
# ------------------------------
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ------------------------------
# 📥 Load Data from Supabase
# ------------------------------
def load_friends():
    try:
        url = f"{SUPABASE_URL}/rest/v1/Friends?select=*"
        res = requests.get(url, headers=HEADERS)
        st.write("DEBUG: Friends API response", res.status_code, res.text)
        data = res.json()
        if isinstance(data, list) and all(isinstance(f, dict) and "name" in f for f in data):
            return [f["name"] for f in data]
        else:
            st.warning("⚠️ Invalid data format for friends list.")
            return []
    except Exception as e:
        st.error(f"❌ Failed to load friends: {e}")
        return []

def add_friend(name):
    try:
        url = f"{SUPABASE_URL}/rest/v1/Friends"
        payload = {"name": name}
        headers = {**HEADERS, "Prefer": "return=representation"}
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code not in [200, 201]:
            st.error(f"❌ Failed to add friend: {res.status_code} - {res.text}")
        else:
            st.success(f"✅ {name} added!")
    except Exception as e:
        st.error(f"❌ Error adding friend: {e}")

def delete_friend(friend_name):
    try:
        url = f"{SUPABASE_URL}/rest/v1/Friends?name=eq.{friend_name}"
        res = requests.delete(url, headers=HEADERS)
        if res.status_code == 204:
            return True
        else:
            st.error(f"❌ Failed to delete friend: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error deleting friend: {e}")
        return False

def load_history():
    try:
        url = f"{SUPABASE_URL}/rest/v1/History?select=id,person1,person2"
        res = requests.get(url, headers=HEADERS)
        st.write("DEBUG: History API response", res.status_code, res.text)
        data = res.json()
        if isinstance(data, list) and all("id" in h and "person1" in h and "person2" in h for h in data):
            return [(h["id"], h["person1"], h["person2"]) for h in data]
        else:
            st.warning("⚠️ Invalid data format for history.")
            return []
    except Exception as e:
        st.error(f"❌ Failed to load history: {e}")
        return []

def add_history(p1, p2):
    try:
        url = f"{SUPABASE_URL}/rest/v1/History"
        payload = {"person1": p1, "person2": p2}
        headers = {**HEADERS, "Prefer": "return=representation"}
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code in [200, 201]:
            record = res.json()[0]
            st.session_state.history.append((record["id"], record["person1"], record["person2"]))
            st.success(f"✅ Added store trip: {p1} & {p2}")
        else:
            st.error(f"❌ Failed to add history: {res.status_code} - {res.text}")
    except Exception as e:
        st.error(f"❌ Error adding history: {e}")

def delete_last_trip():
    if st.session_state.history:
        last_id, p1, p2 = st.session_state.history[-1]
        try:
            url = f"{SUPABASE_URL}/rest/v1/History?id=eq.{last_id}"
            res = requests.delete(url, headers=HEADERS)
            if res.status_code == 204:
                st.session_state.history.pop()
                st.success(f"🗑️ Deleted last trip: {p1} & {p2}")
            else:
                st.error(f"❌ Failed to delete: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"❌ Error deleting last trip: {e}")
    else:
        st.info("No trip to delete.")

# ------------------------------
# 🧠 Session State Bootstrapping
# ------------------------------
if 'friends' not in st.session_state:
    st.session_state.friends = load_friends()
if 'history' not in st.session_state:
    st.session_state.history = load_history()
if 'present_friends' not in st.session_state:
    st.session_state.present_friends = []
if 'excluded_friends' not in st.session_state:
    st.session_state.excluded_friends = []

# ------------------------------
# 🎯 UI STARTS HERE
# ------------------------------
st.title("🥤 NOT IT! – Who's Going to the Store?")

# ➕ Add New Friend
st.subheader("Add a Friend")
new_friend = st.text_input("Add a friend if they are new:")

if st.button("Add Friend"):
    if new_friend.strip() == "":
        st.warning("⚠️ Enter a valid name.")
    elif new_friend.strip() in st.session_state.friends:
        st.info("👀 This friend is already in the list.")
    else:
        add_friend(new_friend.strip())
        st.session_state.friends.append(new_friend.strip())

# 📋 Display All Friends
st.subheader("All Friends")
st.write(st.session_state.friends)

# 🗑️ Delete a Friend
st.subheader("🗑️ Remove a Friend")
if st.session_state.friends:
    friend_to_delete = st.selectbox("Select a friend to delete:", st.session_state.friends)
    if st.button("Delete Friend"):
        if delete_friend(friend_to_delete):
            st.session_state.friends.remove(friend_to_delete)
            if friend_to_delete in st.session_state.present_friends:
                st.session_state.present_friends.remove(friend_to_delete)
            if friend_to_delete in st.session_state.excluded_friends:
                st.session_state.excluded_friends.remove(friend_to_delete)
            st.success(f"✅ {friend_to_delete} deleted.")
else:
    st.write("No friends to delete.")

# ✅ Who's Present Today
st.subheader("Who's Present Today?")
present_selection = st.multiselect("Select who's around today:", st.session_state.friends, default=st.session_state.present_friends)
st.session_state.present_friends = present_selection

# 🙅‍♂️ Exclude Certain Friends (they're present, but won't go)
st.subheader("Exclude Friends (they're present, but won't go)")
excluded_selection = st.multiselect("Exclude these friends from being picked:", st.session_state.present_friends, default=st.session_state.excluded_friends)
st.session_state.excluded_friends = excluded_selection

# 🎲 Pick the Next Two
st.subheader("Pick Who's Going!")

if st.button("Pick Next Two"):
    available_friends = list(set(st.session_state.present_friends) - set(st.session_state.excluded_friends))
    if len(available_friends) < 2:
        st.warning("🚫 Need at least two non-excluded friends to pick from!")
    else:
        recent_pairs = st.session_state.history[-3:]
        recent_people = {person for _, p1, p2 in recent_pairs for person in (p1, p2)}
        final_pool = list(set(available_friends) - recent_people)

        if len(final_pool) < 2:
            st.session_state.history = []
            final_pool = available_friends
            st.info("🔄 Not enough fresh picks. Resetting history.")

        chosen_two = random.sample(final_pool, 2)
        add_history(chosen_two[0], chosen_two[1])

# 🗑️ Delete Last Trip
if st.button("Undo Last Trip"):
    delete_last_trip()

# 📈 Store Visit Count
st.subheader("📊 Store Visit Stats")
if st.session_state.history:
    flat_list = [person for _, p1, p2 in st.session_state.history for person in (p1, p2)]
    counts = Counter(flat_list)
    for friend in st.session_state.friends:
        st.write(f"**{friend}** has gone **{counts.get(friend, 0)}** times.")
else:
    st.write("No visits recorded yet.")

# 📜 Past Pairs History
st.subheader("🕓 Past Store Trips")
if st.session_state.history:
    for i, (_, p1, p2) in enumerate(reversed(st.session_state.history), 1):
        st.write(f"{i}. {p1} & {p2}")
else:
    st.write("No history yet.")
