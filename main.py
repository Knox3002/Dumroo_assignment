import csv
from datetime import datetime, timedelta

# ----------------------------
# 1. Load the dataset
# ----------------------------
def load_data():
    data = []
    with open("dataset.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # convert fields to correct types
            row["grade"] = int(row["grade"])
            row["homework_submitted"] = row["homework_submitted"].lower() == "true"
            row["quiz_date"] = datetime.strptime(row["quiz_date"], "%Y-%m-%d").date()
            row["date"] = datetime.strptime(row["date"], "%Y-%m-%d").date()
            data.append(row)
    return data

# ----------------------------
# 2. Apply role-based filtering
# ----------------------------
def apply_scope(data, grade=None, class_=None, region=None):
    filtered = []
    for d in data:
        if grade and d["grade"] != grade:
            continue
        if class_ and d["class"].upper() != class_.upper():
            continue
        if region and d["region"].lower() != region.lower():
            continue
        filtered.append(d)
    return filtered

# ----------------------------
# 3. Handle user queries
# ----------------------------
def answer_query(data, query):
    query = query.lower().strip()
    today = datetime.now().date()

    if "haven't submitted" in query or "not submitted" in query:
        res = [d["name"] for d in data if not d["homework_submitted"]]
        return "Students who haven't submitted homework: " + ", ".join(res) if res else "All have submitted!"

    elif "performance" in query or "score" in query:
        res = [(d["name"], d["quiz_name"], d["quiz_score"]) for d in data]
        lines = [f"{n} - {q} - {s}" for n, q, s in res]
        return "Performance data:\n" + "\n".join(lines)

    elif "quiz" in query and ("next week" in query or "upcoming" in query):
        next_week = today + timedelta(days=7)
        res = [f"{d['quiz_name']} on {d['quiz_date']} (Grade {d['grade']} {d['class']})"
               for d in data if today <= d["quiz_date"] <= next_week]
        return "Upcoming quizzes:\n" + "\n".join(res) if res else "No upcoming quizzes next week."

    else:
        return "Sorry, I didn't understand the question."

# ----------------------------
# 4. Main loop
# ----------------------------
if __name__ == "__main__":
    data = load_data()

    # Example: an admin assigned to Grade 8, Class A, Region North
    data = apply_scope(data, grade=8, class_="A", region="North")

    print("✅ Dumroo AI Query System Ready!")
    print("Type your question (or 'exit' to quit)\n")

    while True:
        q = input("Ask: ")
        if q.lower() in ("exit", "quit"):
            break
        print(answer_query(data, q))
        print()