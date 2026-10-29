"""
================================================================================
LAYER: PERSISTENCE & BACKEND API LAYER (Database Code & Data Validation)
================================================================================
Architectural Role:
This file serves as the "persistence layer" and backend data controller for the
Student Marks Dashboard.

Persistence Layer Note:
This file encapsulates all data persistence operations (reading, writing, updating,
and deleting records) using pandas and a local CSV file ('students.csv').
Because all data access and computation logic is abstracted behind clean,
standardized Python functions, this persistence layer could later be swapped for
SQLite (or PostgreSQL / SQLAlchemy) without changing any code in app.py.

HTTP Status Codes returned by Backend API methods:
- 200 OK: Data retrieved, query answered, or record successfully deleted.
- 201 Created: New student record created and persisted successfully.
- 400 Bad Request: Input validation failed (empty fields, marks outside 0-100,
  or duplicate roll numbers).
- 404 Not Found: Student record with specified roll number does not exist.
================================================================================
"""

import os
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

# Define the absolute directory path to ensure reliable file resolution
# regardless of whether the app is launched from root or marks_dashboard/
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH: str = os.path.join(BASE_DIR, "students.csv")

# Standard CSV column headers
CSV_COLUMNS: List[str] = ["Roll Number", "Name", "Maths", "Science", "English"]

# 5 Initial sample records seeded automatically on first run
SAMPLE_STUDENTS: List[Dict[str, Any]] = [
    {"Roll Number": "101", "Name": "Aarav Sharma", "Maths": 92.0, "Science": 88.0, "English": 95.0},
    {"Roll Number": "102", "Name": "Diya Patel", "Maths": 78.0, "Science": 84.0, "English": 81.0},
    {"Roll Number": "103", "Name": "Rohan Verma", "Maths": 65.0, "Science": 70.0, "English": 62.0},
    {"Roll Number": "104", "Name": "Sneha Rao", "Maths": 48.0, "Science": 52.0, "English": 44.0},
    {"Roll Number": "105", "Name": "Vikram Singh", "Maths": 35.0, "Science": 55.0, "English": 38.0},
]


# ==============================================================================
# SECTION 1: PERSISTENCE LAYER (CSV FILE I/O WITH PANDAS)
# ==============================================================================

def init_database() -> Dict[str, Any]:
    """
    Initializes the database (students.csv).
    If the file does not exist or is empty, creates it with standard headers
    and seeds 3-5 initial sample records.
    Returns HTTP 200 on success.
    """
    try:
        # Check if file exists and has non-zero size
        if not os.path.exists(CSV_FILE_PATH) or os.path.getsize(CSV_FILE_PATH) == 0:
            # Create a DataFrame from the initial sample records
            seed_df = pd.DataFrame(SAMPLE_STUDENTS, columns=CSV_COLUMNS)
            # Write the seed records to CSV with headers
            seed_df.to_csv(CSV_FILE_PATH, index=False)
            return {
                "status_code": 200,
                "success": True,
                "message": f"Created {CSV_FILE_PATH} and seeded {len(SAMPLE_STUDENTS)} sample records."
            }
        return {
            "status_code": 200,
            "success": True,
            "message": "Database file already exists and is initialized."
        }
    except Exception as exc:
        return {
            "status_code": 500,
            "success": False,
            "message": f"Database initialization failed: {str(exc)}"
        }


def read_raw_data() -> pd.DataFrame:
    """
    Low-level persistence function: Reads the raw CSV file into a pandas DataFrame.
    Ensures Roll Number is treated as a clean string to prevent formatting bugs.
    """
    # Ensure storage is ready before reading
    init_database()
    try:
        # Read CSV with string dtype for Roll Number to preserve leading zeros/formats
        df = pd.read_csv(
            CSV_FILE_PATH,
            dtype={"Roll Number": str, "Name": str},
            keep_default_na=False
        )
        # Ensure marks are numeric (convert coercion to handle bad entries safely)
        for subject in ["Maths", "Science", "English"]:
            if subject in df.columns:
                df[subject] = pd.to_numeric(df[subject], errors="coerce").fillna(0.0)
            else:
                df[subject] = 0.0
        return df
    except Exception:
        # Return empty DataFrame with required columns if file read errors
        return pd.DataFrame(columns=CSV_COLUMNS)


def write_raw_data(df: pd.DataFrame) -> None:
    """
    Low-level persistence function: Writes a pandas DataFrame directly to students.csv.
    """
    # Keep only the canonical columns for storage
    storage_df = df[CSV_COLUMNS].copy()
    storage_df.to_csv(CSV_FILE_PATH, index=False)


# ==============================================================================
# SECTION 2: BUSINESS LOGIC & ACADEMIC CALCULATIONS
# ==============================================================================

def calculate_grade(average: float) -> str:
    """
    Determines student letter grade according to academic rules:
    - A: >= 90
    - B: >= 75 and < 90
    - C: >= 60 and < 75
    - D: >= 40 and < 60
    - F: < 40
    """
    if average >= 90.0:
        return "A"
    elif average >= 75.0:
        return "B"
    elif average >= 60.0:
        return "C"
    elif average >= 40.0:
        return "D"
    else:
        return "F"


def compute_student_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes 'Total', 'Average', and 'Grade' columns for all student records.
    Returns an augmented DataFrame suitable for presentation and analytics.
    """
    if df.empty:
        # Return empty dataframe with computed columns added
        extended_cols = CSV_COLUMNS + ["Total", "Average", "Grade"]
        return pd.DataFrame(columns=extended_cols)

    calc_df = df.copy()

    # Calculate Total marks across Maths, Science, and English (out of 300)
    calc_df["Total"] = calc_df["Maths"] + calc_df["Science"] + calc_df["English"]

    # Calculate Average marks (out of 100) rounded to 2 decimal places
    calc_df["Average"] = (calc_df["Total"] / 3.0).round(2)

    # Assign letter grade based on the Average column
    calc_df["Grade"] = calc_df["Average"].apply(calculate_grade)

    return calc_df


# ==============================================================================
# SECTION 3: BACKEND API & CONTROLLER METHODS (HTTP STATUS RESPONSES)
# ==============================================================================

def get_all_students() -> Dict[str, Any]:
    """
    Backend API: Retrieves all student records enriched with Total, Average, and Grade.
    Returns HTTP 200 OK with DataFrame in the 'data' field.
    """
    raw_df = read_raw_data()
    processed_df = compute_student_metrics(raw_df)
    return {
        "status_code": 200,
        "success": True,
        "message": "Records fetched successfully.",
        "data": processed_df,
        "count": len(processed_df)
    }


def add_student(
    name: str,
    roll_number: str,
    maths: Any,
    science: Any,
    english: Any
) -> Dict[str, Any]:
    """
    Backend API: Validates student input, verifies uniqueness, and saves to students.csv.
    
    Validation Rules:
    - Name cannot be empty or whitespace.
    - Roll Number cannot be empty or whitespace.
    - Maths, Science, and English must be numeric values in range [0, 100].
    - Roll Number must be unique (case-insensitive check).

    Returns:
    - 201 Created on success
    - 400 Bad Request on validation failure or duplicate roll number
    """
    # 1. Validate Name
    if not isinstance(name, str) or not name.strip():
        return {
            "status_code": 400,
            "success": False,
            "message": "Validation Error: Student name cannot be empty."
        }
    clean_name = name.strip()

    # 2. Validate Roll Number
    if not str(roll_number).strip():
        return {
            "status_code": 400,
            "success": False,
            "message": "Validation Error: Roll Number cannot be empty."
        }
    clean_roll = str(roll_number).strip()

    # 3. Validate Marks for each subject
    marks_dict: Dict[str, float] = {}
    subjects_input = [("Maths", maths), ("Science", science), ("English", english)]

    for sub_name, sub_val in subjects_input:
        try:
            val_float = float(sub_val)
        except (ValueError, TypeError):
            return {
                "status_code": 400,
                "success": False,
                "message": f"Validation Error: {sub_name} marks must be a valid number."
            }

        # Ensure marks are within the 0 to 100 boundary
        if val_float < 0.0 or val_float > 100.0:
            return {
                "status_code": 400,
                "success": False,
                "message": f"Validation Error: {sub_name} marks must be between 0 and 100 (received {val_float})."
            }
        marks_dict[sub_name] = round(val_float, 2)

    # 4. Check for duplicate Roll Number in the existing dataset
    df = read_raw_data()
    if not df.empty:
        existing_rolls = df["Roll Number"].astype(str).str.strip().str.lower().tolist()
        if clean_roll.lower() in existing_rolls:
            return {
                "status_code": 400,
                "success": False,
                "message": f"Validation Error: Student with Roll Number '{clean_roll}' already exists."
            }

    # 5. Build new student record and append to database
    new_record = {
        "Roll Number": clean_roll,
        "Name": clean_name,
        "Maths": marks_dict["Maths"],
        "Science": marks_dict["Science"],
        "English": marks_dict["English"]
    }
    new_df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    write_raw_data(new_df)

    return {
        "status_code": 201,
        "success": True,
        "message": f"Student '{clean_name}' (Roll: {clean_roll}) successfully registered.",
        "data": new_record
    }


def delete_student(roll_number: str) -> Dict[str, Any]:
    """
    Backend API (Stretch Goal): Deletes a student by Roll Number from students.csv.
    
    Returns:
    - 200 OK: Student found and deleted.
    - 400 Bad Request: Empty roll number supplied.
    - 404 Not Found: Roll number not present in the database.
    """
    clean_roll = str(roll_number).strip()
    if not clean_roll:
        return {
            "status_code": 400,
            "success": False,
            "message": "Validation Error: Roll number to delete must be specified."
        }

    df = read_raw_data()
    if df.empty:
        return {
            "status_code": 404,
            "success": False,
            "message": f"Not Found: No records exist. Student '{clean_roll}' not found."
        }

    # Check if student exists
    match_mask = df["Roll Number"].astype(str).str.strip().str.lower() == clean_roll.lower()
    if not match_mask.any():
        return {
            "status_code": 404,
            "success": False,
            "message": f"Not Found: Student with Roll Number '{clean_roll}' was not found."
        }

    # Get student name before deleting for nice user feedback
    student_name = df.loc[match_mask, "Name"].values[0]

    # Filter out the matching record
    updated_df = df[~match_mask].copy()
    write_raw_data(updated_df)

    return {
        "status_code": 200,
        "success": True,
        "message": f"Student '{student_name}' (Roll: {clean_roll}) successfully deleted."
    }


def get_analytics() -> Dict[str, Any]:
    """
    Backend API: Computes statistical summaries, topper info, subject averages,
    and pass/fail metrics.
    Returns HTTP 200 OK with analytics data structure.
    """
    raw_df = read_raw_data()
    df = compute_student_metrics(raw_df)

    if df.empty:
        return {
            "status_code": 200,
            "success": True,
            "data": {
                "total_students": 0,
                "class_average": 0.0,
                "toppers": [],
                "subject_averages": {"Maths": 0.0, "Science": 0.0, "English": 0.0},
                "subject_pass_fail": {
                    "Maths": {"pass": 0, "fail": 0, "pass_rate": 0.0},
                    "Science": {"pass": 0, "fail": 0, "pass_rate": 0.0},
                    "English": {"pass": 0, "fail": 0, "pass_rate": 0.0},
                },
                "grade_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
            }
        }

    total_students = len(df)
    class_average = round(float(df["Average"].mean()), 2)

    # Find the topper(s) - maximum Total marks
    max_total = df["Total"].max()
    topper_rows = df[df["Total"] == max_total]
    toppers = topper_rows.to_dict(orient="records")

    # Subject averages
    subject_averages = {
        "Maths": round(float(df["Maths"].mean()), 2),
        "Science": round(float(df["Science"].mean()), 2),
        "English": round(float(df["English"].mean()), 2),
    }

    # Subject-wise pass/fail metrics (Passing mark is >= 40)
    pass_mark = 40.0
    subject_pass_fail = {}
    for sub in ["Maths", "Science", "English"]:
        passed = int((df[sub] >= pass_mark).sum())
        failed = int((df[sub] < pass_mark).sum())
        pass_rate = round((passed / total_students) * 100.0, 1) if total_students > 0 else 0.0
        subject_pass_fail[sub] = {
            "pass": passed,
            "fail": failed,
            "pass_rate": pass_rate
        }

    # Grade distribution counts
    grade_counts = df["Grade"].value_counts().to_dict()
    grade_distribution = {g: int(grade_counts.get(g, 0)) for g in ["A", "B", "C", "D", "F"]}

    return {
        "status_code": 200,
        "success": True,
        "data": {
            "total_students": total_students,
            "class_average": class_average,
            "toppers": toppers,
            "subject_averages": subject_averages,
            "subject_pass_fail": subject_pass_fail,
            "grade_distribution": grade_distribution
        }
    }
