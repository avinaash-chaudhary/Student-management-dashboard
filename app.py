"""EduDesk: a student management dashboard built with Python and Streamlit.

Students, teachers and grades are stored in school_data.json (next to this
file). The file is created automatically on the first run.

Run:  streamlit run app.py
"""

import copy
import json
import re
from pathlib import Path
from statistics import mean

import pandas as pd
import streamlit as st

st.set_page_config(page_title="EduDesk", page_icon="🎓", layout="wide")

DATA_FILE = Path(__file__).parent / "school_data.json"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CHART_COLOR = "#2F6B5A"

DEFAULT_DATA = {
    "students": [
        {
            "name": "Avi",
            "age": 12,
            "email": "asad@gmail.com",
            "roll_no": "1",
            "grade": {"Math": 92.0},
        },
        {
            "name": "Ad",
            "age": 13,
            "email": "ad@gmail.com",
            "roll_no": "2",
            "grade": {},
        },
    ],
    "teachers": [
        {
            "name": "Ajay",
            "age": 30,
            "email": "ajay@gmail.com",
            "subject": "Math",
            "emp_id": "07",
        }
    ],
}


# ─── Data layer ───────────────────────────────────────────────────────────────
def save_data(data: dict) -> None:
    """Write to a temp file first, then swap it in (an atomic write), so a crash
    in the middle of saving can never leave school_data.json half written."""
    tmp = DATA_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    tmp.replace(DATA_FILE)


def load_data() -> dict:
    if not DATA_FILE.exists():
        save_data(DEFAULT_DATA)
        return copy.deepcopy(DEFAULT_DATA)
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        data.setdefault("students", [])
        data.setdefault("teachers", [])
        for student in data["students"]:
            student.setdefault("grade", {})
    except (OSError, ValueError, TypeError, AttributeError) as err:
        st.error(
            f"Could not read {DATA_FILE.name} ({err}). "
            "Fix the file, or delete it to start with sample data."
        )
        st.stop()
    return data


def student_average(student: dict):
    grades = student["grade"]
    return round(mean(grades.values()), 1) if grades else None


def all_subjects(data: dict) -> list:
    subjects = {t["subject"] for t in data["teachers"] if t.get("subject")}
    for student in data["students"]:
        subjects.update(student["grade"])
    return sorted(subjects)


def students_df(data: dict) -> pd.DataFrame:
    rows = [
        {
            "Roll no": s.get("roll_no", ""),
            "Name": s.get("name", ""),
            "Age": s.get("age"),
            "Email": s.get("email", ""),
            "Subjects": ", ".join(s["grade"]) or "-",
            "Average": student_average(s),
        }
        for s in data["students"]
    ]
    columns = ["Roll no", "Name", "Age", "Email", "Subjects", "Average"]
    return pd.DataFrame(rows, columns=columns)


def teachers_df(data: dict) -> pd.DataFrame:
    rows = [
        {
            "Employee ID": t.get("emp_id", ""),
            "Name": t.get("name", ""),
            "Age": t.get("age"),
            "Email": t.get("email", ""),
            "Subject": t.get("subject", ""),
            "Students graded": sum(
                1 for s in data["students"] if t.get("subject") in s["grade"]
            ),
        }
        for t in data["teachers"]
    ]
    columns = ["Employee ID", "Name", "Age", "Email", "Subject", "Students graded"]
    return pd.DataFrame(rows, columns=columns)


# ─── UI helpers ───────────────────────────────────────────────────────────────
def form_key(name: str) -> str:
    """Widget keys change after every successful save, so the next form opens
    with blank fields. Failed submits keep the key, so typed text is not lost."""
    return f"{name}_{st.session_state.get(f'_v_{name}', 0)}"


def reset_form(name: str) -> None:
    st.session_state[f"_v_{name}"] = st.session_state.get(f"_v_{name}", 0) + 1


def flash(message: str) -> None:
    st.session_state["_flash"] = message


def show_flash() -> None:
    if "_flash" in st.session_state:
        st.success(st.session_state.pop("_flash"))


def commit(data: dict, message: str) -> None:
    """Save, queue a confirmation message, then rerun so every widget shows the
    new data. The message lives in session_state because a rerun wipes anything
    drawn on screen."""
    try:
        save_data(data)
    except OSError as err:
        st.error(f"Could not save your changes: {err}")
        return
    flash(message)
    st.rerun()


# ─── Pages ────────────────────────────────────────────────────────────────────
def page_dashboard(data: dict) -> None:
    st.title("Dashboard")
    show_flash()
    students, teachers = data["students"], data["teachers"]

    marks_by_subject = {}
    for student in students:
        for subject, marks in student["grade"].items():
            marks_by_subject.setdefault(subject, []).append(marks)
    all_marks = [m for marks in marks_by_subject.values() for m in marks]

    cards = [
        ("Students", len(students)),
        ("Teachers", len(teachers)),
        ("Subjects", len(all_subjects(data))),
        ("Average marks", f"{mean(all_marks):.1f}" if all_marks else "-"),
    ]
    for col, (label, value) in zip(st.columns(4), cards):
        with col.container(border=True):
            st.metric(label, value)

    left, right = st.columns(2)
    with left:
        st.subheader("Average marks by subject")
        if marks_by_subject:
            averages = pd.Series(
                {k: round(mean(v), 1) for k, v in marks_by_subject.items()},
                name="Average marks",
            )
            st.bar_chart(averages, color=CHART_COLOR, y_label="Average marks")
        else:
            st.info("No grades yet. Add marks from the Students page.")
    with right:
        st.subheader("Students by age")
        if students:
            ages = pd.Series([s.get("age") for s in students]).value_counts()
            st.bar_chart(
                ages.sort_index(), color=CHART_COLOR, x_label="Age", y_label="Students"
            )
        else:
            st.info("No students yet. Add the first one from the Students page.")

    top, waiting = st.columns(2)
    with top:
        st.subheader("Top performers")
        ranked = sorted(
            (s for s in students if s["grade"]), key=student_average, reverse=True
        )
        if ranked:
            table = pd.DataFrame(
                [
                    {
                        "Rank": i,
                        "Name": s.get("name", ""),
                        "Roll no": s.get("roll_no", ""),
                        "Average": student_average(s),
                    }
                    for i, s in enumerate(ranked[:5], start=1)
                ]
            )
            st.dataframe(table, hide_index=True)
        else:
            st.info("Rankings appear once a student has a grade.")
    with waiting:
        st.subheader("Waiting for grades")
        ungraded = [s for s in students if not s["grade"]]
        if ungraded:
            table = pd.DataFrame(
                [{"Name": s.get("name", ""), "Roll no": s.get("roll_no", "")} for s in ungraded]
            )
            st.dataframe(table, hide_index=True)
        elif students:
            st.success("Every student has at least one grade.")
        else:
            st.info("No students yet.")


def page_students(data: dict) -> None:
    st.title("Students")
    show_flash()
    students = data["students"]

    query = st.text_input(
        "Search students",
        placeholder="Search by name, roll no or email",
        label_visibility="collapsed",
    )
    df = students_df(data)
    if query.strip():
        text = df[["Roll no", "Name", "Email"]].astype(str)
        hits = text.apply(
            lambda col: col.str.contains(query.strip(), case=False, regex=False)
        ).any(axis=1)
        df = df[hits]
    if df.empty:
        st.info(
            "No students match your search."
            if students
            else "No students yet. Add the first one below."
        )
    else:
        st.dataframe(
            df,
            hide_index=True,
            column_config={"Average": st.column_config.NumberColumn(format="%.1f")},
        )

    with st.expander("Add a student", expanded=not students):
        k = form_key("add_student")
        with st.form(k):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full name", max_chars=60, key=f"{k}_name")
            roll_no = c2.text_input("Roll no", max_chars=20, key=f"{k}_roll")
            age = c1.number_input(
                "Age", min_value=3, max_value=25, value=12, step=1, key=f"{k}_age"
            )
            email = c2.text_input("Email", max_chars=80, key=f"{k}_email")
            submitted = st.form_submit_button("Add student", type="primary")
        if submitted:
            name, roll_no, email = name.strip(), roll_no.strip(), email.strip()
            errors = []
            if not name:
                errors.append("Enter the student's full name.")
            if not roll_no:
                errors.append("Enter a roll no.")
            elif any(s.get("roll_no") == roll_no for s in students):
                errors.append(f"Roll no {roll_no} is already taken. Use a different one.")
            if not EMAIL_RE.match(email):
                errors.append("Enter a valid email, like name@example.com.")
            for message in errors:
                st.error(message)
            if not errors:
                students.append(
                    {
                        "name": name,
                        "age": int(age),
                        "email": email,
                        "roll_no": roll_no,
                        "grade": {},
                    }
                )
                reset_form("add_student")
                commit(data, f"Added {name} with roll no {roll_no}.")

    if not students:
        return

    st.divider()
    st.subheader("Student profile")
    by_roll = {s.get("roll_no", ""): s for s in students}
    selected = st.selectbox(
        "Choose a student",
        list(by_roll),
        format_func=lambda r: f"{r} - {by_roll[r].get('name', '')}",
    )
    student = by_roll[selected]
    grades = student["grade"]
    k = form_key(f"profile_{selected}")

    with st.container(border=True):
        st.markdown(f"### {student.get('name', '')}")
        a, b, c, d = st.columns(4)
        a.metric("Roll no", selected)
        b.metric("Age", student.get("age", "-"))
        c.metric("Subjects", len(grades))
        average = student_average(student)
        d.metric("Average marks", "-" if average is None else average)
        st.caption(student.get("email", ""))

    if grades:
        grade_df = pd.DataFrame({"Subject": list(grades), "Marks": list(grades.values())})
        st.dataframe(
            grade_df,
            hide_index=True,
            column_config={
                "Marks": st.column_config.ProgressColumn(
                    "Marks", min_value=0, max_value=100, format="%.1f"
                )
            },
        )
    else:
        st.info(f"{student.get('name', 'This student')} has no grades yet. Add the first one below.")

    with st.form(f"{k}_grade"):
        st.markdown("**Add or update a grade**")
        c1, c2, c3 = st.columns(3)
        picked = c1.selectbox(
            "Subject",
            all_subjects(data),
            index=None,
            placeholder="Choose a subject",
            key=f"{k}_picked",
        )
        typed = c2.text_input("Or add a new subject", max_chars=40, key=f"{k}_typed")
        marks = c3.number_input(
            "Marks out of 100",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.5,
            key=f"{k}_marks",
        )
        save_grade = st.form_submit_button("Save grade", type="primary")
    if save_grade:
        subject = typed.strip() or picked
        if not subject:
            st.error("Choose a subject or type a new one.")
        else:
            grades[subject] = float(marks)
            reset_form(f"profile_{selected}")
            commit(data, f"Saved {subject}: {marks:g} for {student.get('name', selected)}.")

    if grades:
        with st.expander("Remove a grade"):
            to_remove = st.selectbox("Subject", list(grades), key=f"{k}_rm")
            if st.button("Remove grade", key=f"{k}_rmbtn", icon=":material/delete:"):
                del grades[to_remove]
                reset_form(f"profile_{selected}")
                commit(data, f"Removed {to_remove} from {student.get('name', selected)}.")

    with st.expander("Delete this student"):
        st.warning(
            f"This permanently removes {student.get('name', selected)} and all their grades."
        )
        sure = st.checkbox("I understand, delete this student", key=f"{k}_sure")
        if st.button(
            "Delete student", key=f"{k}_del", disabled=not sure, icon=":material/delete:"
        ):
            data["students"] = [s for s in students if s is not student]
            commit(data, f"Deleted {student.get('name', selected)}.")


def page_teachers(data: dict) -> None:
    st.title("Teachers")
    show_flash()
    teachers = data["teachers"]

    df = teachers_df(data)
    if df.empty:
        st.info("No teachers yet. Add the first one below.")
    else:
        st.dataframe(df, hide_index=True)

    with st.expander("Add a teacher", expanded=not teachers):
        k = form_key("add_teacher")
        with st.form(k):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full name", max_chars=60, key=f"{k}_name")
            emp_id = c2.text_input("Employee ID", max_chars=20, key=f"{k}_emp")
            subject = c1.text_input("Subject", max_chars=40, key=f"{k}_subject")
            age = c2.number_input(
                "Age", min_value=18, max_value=70, value=30, step=1, key=f"{k}_age"
            )
            email = c1.text_input("Email", max_chars=80, key=f"{k}_email")
            submitted = st.form_submit_button("Add teacher", type="primary")
        if submitted:
            name, emp_id = name.strip(), emp_id.strip()
            subject, email = subject.strip(), email.strip()
            errors = []
            if not name:
                errors.append("Enter the teacher's full name.")
            if not emp_id:
                errors.append("Enter an employee ID.")
            elif any(t.get("emp_id") == emp_id for t in teachers):
                errors.append(f"Employee ID {emp_id} is already taken. Use a different one.")
            if not subject:
                errors.append("Enter the subject this teacher teaches.")
            if not EMAIL_RE.match(email):
                errors.append("Enter a valid email, like name@example.com.")
            for message in errors:
                st.error(message)
            if not errors:
                teachers.append(
                    {
                        "name": name,
                        "age": int(age),
                        "email": email,
                        "subject": subject,
                        "emp_id": emp_id,
                    }
                )
                reset_form("add_teacher")
                commit(data, f"Added {name} ({subject}).")

    if teachers:
        with st.expander("Remove a teacher"):
            kr = form_key("remove_teacher")
            by_id = {t.get("emp_id", ""): t for t in teachers}
            chosen = st.selectbox(
                "Teacher",
                list(by_id),
                format_func=lambda i: f"{i} - {by_id[i].get('name', '')}",
                key=f"{kr}_pick",
            )
            sure = st.checkbox("I understand, remove this teacher", key=f"{kr}_sure")
            if st.button(
                "Remove teacher", key=f"{kr}_btn", disabled=not sure, icon=":material/delete:"
            ):
                removed = by_id[chosen]
                data["teachers"] = [t for t in teachers if t is not removed]
                reset_form("remove_teacher")
                commit(data, f"Removed {removed.get('name', chosen)}.")


def page_data(data: dict) -> None:
    st.title("Data")
    show_flash()
    st.caption(f"Everything is saved in {DATA_FILE.name}, next to app.py.")

    st.download_button(
        "Download school_data.json",
        json.dumps(data, indent=4, ensure_ascii=False),
        file_name="school_data.json",
        mime="application/json",
        icon=":material/download:",
    )
    st.json(data, expanded=2)

    with st.expander("Restore sample data"):
        kr = form_key("restore")
        st.warning("This replaces all students and teachers with the original sample records.")
        sure = st.checkbox("I understand, restore the sample data", key=f"{kr}_sure")
        if st.button("Restore sample data", key=f"{kr}_btn", disabled=not sure):
            reset_form("restore")
            commit(copy.deepcopy(DEFAULT_DATA), "Sample data restored.")


# ─── App shell ────────────────────────────────────────────────────────────────
PAGES = {
    "Dashboard": page_dashboard,
    "Students": page_students,
    "Teachers": page_teachers,
    "Data": page_data,
}

with st.sidebar:
    st.header("EduDesk")
    st.caption("Student management for a small school")
    page = st.radio("Go to", list(PAGES), label_visibility="collapsed")
    st.divider()
    st.caption("Built with Python and Streamlit")

PAGES[page](load_data())