import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, timedelta

# ----------------------------
# 1. Load data
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("dataset.csv", parse_dates=["quiz_date", "date"])
    return df

df = load_data()

# ----------------------------
# 2. Role-based filter (grade/class/region)
# ----------------------------
def apply_scope(df, grade=None, class_=None, region=None):
    filtered = df.copy()
    if grade:
        filtered = filtered[filtered["grade"] == grade]
    if class_:
        filtered = filtered[filtered["class"].str.upper() == class_.upper()]
    if region:
        filtered = filtered[filtered["region"].str.lower() == region.lower()]
    return filtered

# ----------------------------
# 3. Hugging Face API query
# ----------------------------
def ask_huggingface(question):
    model = "mistralai/Mistral-7B-Instruct-v0.2"
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {os.environ.get('HUGGINGFACEHUB_API_TOKEN')}"}
    payload = {"inputs": question}

    response = requests.post(api_url, headers=headers, json=payload)
    try:
        data = response.json()
        # Extract model reply
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        elif "generated_text" in data:
            return data["generated_text"]
        else:
            return str(data)
    except Exception as e:
        return f"Error: {e}"

# ----------------------------
# 4. Interpret query (simple fallback logic)
# ----------------------------
def handle_query(df, question):
    q = question.lower()
    today = datetime.now().date()

    if "homework" in q and ("not" in q or "haven't" in q):
        res = df[df["homework_submitted"] == False]["name"].tolist()
        return "Students who haven't submitted homework:\n" + ", ".join(res)

    elif "performance" in q or "score" in q:
        res = df[["name", "quiz_name", "quiz_score"]]
        return "Performance data:\n" + res.to_string(index=False)

    elif "quiz" in q and ("next week" in q or "upcoming" in q):
        next_week = today + timedelta(days=7)
        res = df[(df["quiz_date"].dt.date >= today) & (df["quiz_date"].dt.date <= next_week)]
        if res.empty:
            return "No upcoming quizzes next week."
        return "Upcoming quizzes:\n" + res[["quiz_name", "quiz_date", "grade", "class"]].to_string(index=False)

    else:
        # If not a known pattern, ask model
        return ask_huggingface(question)

# ----------------------------
# 5. Streamlit UI
# ----------------------------
st.title("🎓 Dumroo AI Query System")
st.write("Ask questions about your students or classes in plain English.")

grade = st.number_input("Your grade (e.g. 8)", min_value=1, max_value=12, step=1, value=8)
class_ = st.text_input("Your class (e.g. A)", value="A")
region = st.text_input("Your region (e.g. North)", value="North")

filtered_df = apply_scope(df, grade, class_, region)

query = st.text_input("Ask your question:")

if st.button("Submit"):
    with st.spinner("Thinking..."):
        answer = handle_query(filtered_df, query)
    st.success("Answer:")
    st.text(answer)