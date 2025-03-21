import streamlit as st
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import Counter

# ------------------------------
# 🔐 Google Sheets Setup
# ------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1tEVgicVN-2y94cai6GHTeUGDHjxjQUckqvmHDz-8Pds/edit#gid=0"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)

try:
    gc = gspread.authorize(CREDENTIALS)
    sheet = gc.open_by_url(SHEET_URL).sheet1
except Exception as e:
    st.error(f"❌ Error connecting to Google Sheets: {e}")
    st.stop()

# ------------------------------
# 📥 Load Data from Google Sheet
# ------------------------------
def load_data():
    try:
        data = sheet.get_all_values()
        if not data or len(data[0]) == 0:
            return [], []
        friends = data[0]
        history = [tuple(row) for row in data[1:] if len(row) == 2]
        return friends, history
    except Exception as e:
        st.error(f"❌ Failed to load data from Google Sheets: {e}")
        return [], []

# ------------------------------
# 💾 Save Data to Google Sheet
# ------------------------------
def save_data(friends, history):
    try:
        new_data = [friends] + [list(pair) for pair in history]
        sheet.clear()
        sheet.append_rows(new_data)
    except Exception as e:
        st.error(f"❌ Failed to save data to Google Sheets: {e}")

# ------------------------------
# 🧠 Session State Bootstrapping
# ------------------------------
if 'friends' not in st.session_state:
    st.session_state.friends, st.session_state.history = load_data()
if 'present_friends' not in st.session_state:
    st.session_state.present_friends = []
if 'excluded_friends' not in st.session_state:
    st.session_state.excluded_friends = []

# ------------------------------
# 🎯 UI STARTS HERE
# ------------------------------
st.title("🥤 NOT IT! – Who's Going to the Store?")

# ------------------------------
# ➕ Add New Friend
# ------------------------------
st.subheader("Add a Friend")
new_friend = st.text_input("Add a friend if they are new:")

if st.button("Add Friend"):
    if new_friend.strip() == "":
        st.warning("⚠️ Enter a valid name.")
    elif new_friend in st.session_state.friends:
        st.info("👀 This friend is already in the list.")
    else:
        st.session_state.friends.append(new_friend.strip())
        save_data(st.session_state.friends, st.session_state.history)
        st.success(f"✅ {new_friend} added!")

# ------------------------------
# 📋 Display All Friends
# ------------------------------
st.subheader("All Friends")
st.write(st.session_state.friends)

# ------------------------------
# ✅ Who's Present Today
# ------------------------------
st.subheader("Who's Present Today?")
present_selection = st.multiselect("Select who's around today:", st.session_state.friends, default=st.session_state.present_friends)
st.session_state.present_friends = present_selection

# ------------------------------
# 🙅‍♂️ Exclude Certain Friends (not willing to go)
# ------------------------------
st.subheader("Exclude Friends (they're present, but won't go)")
excluded_selection = st.multiselect("Exclude these friends from being picked:", st.session_state.present_friends, default=st.session_state.excluded_friends)
st.session_state.excluded_friends = excluded_selection

# ------------------------------
# 🎲 Pick the Next Two
# ------------------------------
st.subheader("Pick Who's Going!")

if st.button("Pick Next Two"):
    available_friends = list(set(st.session_state.present_friends) - set(st.session_state.excluded_friends))
    if len(available_friends) < 2:
        st.warning("🚫 Need at least two non-excluded friends to pick from!")
    else:
        recent_pairs = st.session_state.history[-3:]  # Last 3 pairs
        recent_people = {person for pair in recent_pairs for person in pair}
        final_pool = list(set(available_friends) - recent_people)

        if len(final_pool) < 2:
            st.session_state.history = []
            final_pool = available_friends
            st.info("🔄 Not enough fresh picks. Resetting history.")

        chosen_two = random.sample(final_pool, 2)
        st.session_state.history.append(tuple(chosen_two))
        save_data(st.session_state.friends, st.session_state.history)

        st.success(f"🎉 Next to go: **{chosen_two[0]}** and **{chosen_two[1]}**")

# ------------------------------
# 📈 Store Visit Count
# ------------------------------
st.subheader("📊 Store Visit Stats")
if st.session_state.history:
    flat_list = [person for pair in st.session_state.history for person in pair]
    counts = Counter(flat_list)
    for friend in st.session_state.friends:
        st.write(f"**{friend}** has gone **{counts.get(friend, 0)}** times.")
else:
    st.write("No visits recorded yet.")

# ------------------------------
# 📜 Past Pairs History
# ------------------------------
st.subheader("🕓 Past Store Trips")
if st.session_state.history:
    for i, pair in enumerate(reversed(st.session_state.history), 1):
        st.write(f"{i}. {pair[0]} & {pair[1]}")
else:
    st.write("No history yet.")
