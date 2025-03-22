# 🥤 NOT IT! – Who's Going to the Store?

A fun little web app to decide **which two friends are going to the store today** — because nobody wants to volunteer 😂

This app uses **Streamlit** as the frontend and **Supabase** as the cloud backend (PostgreSQL) to store friend lists and visit history.

---

## ⚡ Features

- ➕ Add friends to the list
- ✅ Mark who's present today
- 🙅‍♂️ Exclude friends who refuse to go
- 🎲 Randomly pick two people to go to the store
- 📈 See how many times each friend has gone
- 🕓 View past trip history
- 🗑️ Undo last trip
- ❌ Delete any friend from the list

---

## 💻 Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | [Streamlit](https://streamlit.io) |
| Backend | [Supabase (PostgreSQL + REST API)](https://supabase.com) |
| Hosting | [Streamlit Cloud](https://streamlit.io/cloud) |

---

## 🚀 Getting Started (Run Locally)

1. Clone the repo
```bash
git clone https://github.com/your-username/roster-app.git
cd roster-app
```

2. Run the streamlit app:
```
streamlit run app.py
```

3. Access the App at http://localhost:8501 in your browser.
