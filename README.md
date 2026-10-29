# 🎓 Student Marks Dashboard

A lightweight, beginner-friendly, and modular web application built with **Streamlit** and **pandas** to record, analyze, and manage student academic performance locally on your laptop.

---

## 🌟 Features

1. **Student Registration Form (Sidebar)**:
   - Input student name, roll number, and marks for **Maths**, **Science**, and **English** (validated strictly within 0–100).
   - Validates uniqueness of roll number and non-empty inputs.
   - Provides instant HTTP status code feedback (`201 Created` or `400 Bad Request`).
2. **Persistent CSV Storage (`students.csv`)**:
   - Reads and writes records using `pandas`.
   - Automatically initializes and seeds **5 realistic sample student records** on first launch if `students.csv` does not exist.
3. **Academic Calculations & Data Table**:
   - Calculates **Total** (out of 300), **Average** (out of 100), and **Grade** for every student:
     - **A**: Average ≥ 90
     - **B**: 75 ≤ Average < 90
     - **C**: 60 ≤ Average < 75
     - **D**: 40 ≤ Average < 60
     - **F**: Average < 40 (Fail)
   - Interactive table with real-time search (by name/roll number) and grade filtering.
4. **Highlighted Class Topper Card**:
   - Prominent trophy card displaying top student(s), total score, average percentage, and individual subject breakdown.
5. **Subject Average Bar Chart**:
   - Visual bar chart displaying class average marks across Mathematics, Science, and English.
6. **CSV Export Button**:
   - Download the full computed grade sheet as `student_marks_report.csv` directly from the browser.
7. **Stretch Goals Included**:
   - 🗑️ **Delete Student Record**: Select a student by roll number to safely delete them from the CSV database (`200 OK` or `404 Not Found`).
   - 🥧 **Subject-wise Pass/Fail Pie Chart**: Interactive pie chart displaying the exact pass (≥40) vs fail (<40) ratio for any selected subject.

---

## 🏗️ Architecture & Layer Separation

The application strictly follows a clean three-tier separation of concerns:

| Layer | File | Description |
|---|---|---|
| **Frontend / Presentation Layer** | [`app.py`](file:///c:/Users/HP/Desktop/gen%20ai%20exercises/day%207.1/marks_dashboard/app.py) | Streamlit UI containing forms, KPI metric cards, data tables, visual charts, and feedback alerts. Contains **no** direct file I/O. |
| **Backend API & Controller** | [`data_store.py`](file:///c:/Users/HP/Desktop/gen%20ai%20exercises/day%207.1/marks_dashboard/data_store.py) | Business logic, input validation, grade computation, and standard HTTP-like status code responses (`200`, `201`, `400`, `404`). |
| **Database / Persistence Layer** | [`data_store.py`](file:///c:/Users/HP/Desktop/gen%20ai%20exercises/day%207.1/marks_dashboard/data_store.py) & [`students.csv`](file:///c:/Users/HP/Desktop/gen%20ai%20exercises/day%207.1/marks_dashboard/students.csv) | Low-level CSV read/write functions using pandas. **Can later be swapped for SQLite without altering `app.py`**. |

---

## 📁 Folder Structure

```
marks_dashboard/
├── app.py             # Frontend presentation layer (Streamlit UI)
├── data_store.py      # Persistence layer & backend API methods
├── students.csv       # CSV database (created & seeded on first run)
├── requirements.txt   # Pinned open-source library dependencies
└── README.md          # Project documentation and quickstart guide
```

---

## ⚙️ Prerequisites

- **Python**: Version `3.9` or higher (tested on Python `3.12`)
- **OS**: Windows, macOS, or Linux
- **Web Browser**: Any modern browser (Chrome, Edge, Firefox, Safari)

---

## 🚀 Installation & Setup

### 1. Open your terminal or PowerShell and navigate to the project folder:
```bash
cd "c:\Users\HP\Desktop\gen ai exercises\day 7.1\marks_dashboard"
```

*(Optional but recommended) Create and activate a Python virtual environment:*
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install pinned dependencies:
```bash
pip install -r requirements.txt
```

---

## 💻 How to Run

Launch the Streamlit web server:

```bash
# If your terminal is inside marks_dashboard/
streamlit run app.py

# Or if your terminal is in the project root:
streamlit run marks_dashboard/app.py
```

### 🌐 Access URL
Once started, Streamlit will display local and network URLs. Open the following in your browser:

👉 **[http://localhost:8501](http://localhost:8501)**

---

## 📡 Backend HTTP Status Codes

All backend functions in [`data_store.py`](file:///c:/Users/HP/Desktop/gen%20ai%20exercises/day%207.1/marks_dashboard/data_store.py) return structured responses with standard HTTP status codes consumed by [`app.py`](file:///c:/Users/HP/Desktop/gen%20ai%20exercises/day%207.1/marks_dashboard/app.py):

| Code | Status | Meaning in Application |
|---|---|---|
| `200` | **OK** | Student list or analytics retrieved successfully; student record deleted successfully. |
| `201` | **Created** | New student record validated and appended to `students.csv`. |
| `400` | **Bad Request** | Input validation failed (empty name/roll number, marks < 0 or > 100, or duplicate roll number). |
| `404` | **Not Found** | Student roll number not found in `students.csv` when attempting deletion. |

---

## 🔄 Swapping to SQLite (Future Extension)

Because all storage operations are abstracted in [`data_store.py`](file:///c:/Users/HP/Desktop/gen%20ai%20exercises/day%207.1/marks_dashboard/data_store.py), moving to an SQLite database or PostgreSQL requires only updating the internal database connection and queries in `data_store.py`. **The frontend code in `app.py` remains 100% unchanged.**

---

## 📄 License & Tools

Built entirely with free, open-source Python tools:
- [Streamlit](https://streamlit.io/)
- [pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Altair](https://altair-viz.github.io/)
