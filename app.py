"""
================================================================================
LAYER: PRESENTATION / FRONTEND LAYER (Streamlit User Interface)
================================================================================
Architectural Role:
This file represents the Presentation / Frontend Layer for the Student Marks
Dashboard. It is built using Streamlit to provide an interactive, responsive,
and user-friendly web interface for local laptops.

Separation of Concerns:
This layer contains ZERO low-level database or CSV reading/writing code.
All data queries, record mutations, validation, and analytics are delegated to
the Backend & Persistence Layer ('data_store.py'). The UI reacts to the standard
HTTP status codes (200, 201, 400, 404) returned by data_store.
================================================================================
"""

import os
import sys
from typing import Dict, Any
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Ensure the local marks_dashboard directory is on sys.path for direct imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Import the persistence and backend API layer
import data_store


# ==============================================================================
# SECTION 1: PAGE CONFIGURATION & STYLING
# ==============================================================================

# Set Streamlit page options (tab title, icon, and wide responsive layout)
st.set_page_config(
    page_title="Student Marks Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, professional UI styling
st.markdown("""
<style>
    /* Main container styling */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
    }

    /* Metric cards styling */
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* Highlighted Topper Card styling */
    .topper-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #f59e0b;
        border-radius: 16px;
        padding: 22px 26px;
        box-shadow: 0 6px 18px rgba(245, 158, 11, 0.18);
        position: relative;
        overflow: hidden;
        margin-bottom: 24px;
    }
    .topper-badge {
        display: inline-block;
        background-color: #d97706;
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-bottom: 8px;
    }
    .topper-name {
        font-size: 1.75rem;
        font-weight: 800;
        color: #78350f;
        margin-bottom: 6px;
    }
    .topper-stats {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 10px;
    }
    .topper-stat-item {
        background: rgba(255, 255, 255, 0.75);
        border: 1px solid #fde68a;
        border-radius: 8px;
        padding: 8px 14px;
    }
    .topper-stat-label {
        font-size: 0.75rem;
        color: #92400e;
        font-weight: 600;
    }
    .topper-stat-val {
        font-size: 1.25rem;
        font-weight: 700;
        color: #78350f;
    }

    /* Grade badge helper */
    .grade-pill {
        display: inline-block;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
    }
    .grade-A { background: #dcfce7; color: #166534; }
    .grade-B { background: #dbeafe; color: #1e40af; }
    .grade-C { background: #fef9c3; color: #854d0e; }
    .grade-D { background: #ffedd5; color: #9a3412; }
    .grade-F { background: #fee2e2; color: #991b1b; }

    /* Section divider & headers */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 12px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SECTION 2: SIDEBAR - INPUT FORM & ACTIONS (ADD / DELETE)
# ==============================================================================

st.sidebar.title("🎒 Portal Controls")
st.sidebar.caption("Separated Architecture: Frontend ➡️ Backend ➡️ Persistence")

# Sub-section 2.1: Add Student Form
st.sidebar.markdown("### 📝 Register New Student")
with st.sidebar.form(key="add_student_form", clear_on_submit=False):
    # Student identity inputs
    student_name = st.text_input("Student Name *", placeholder="e.g. Ananya Sen")
    roll_number = st.text_input("Roll Number *", placeholder="e.g. 106")

    st.markdown("**Subject Marks (0 to 100)**")
    # Marks inputs with default value and strict range bounds
    maths_marks = st.number_input("Maths Marks", min_value=0.0, max_value=100.0, value=75.0, step=1.0)
    science_marks = st.number_input("Science Marks", min_value=0.0, max_value=100.0, value=75.0, step=1.0)
    english_marks = st.number_input("English Marks", min_value=0.0, max_value=100.0, value=75.0, step=1.0)

    # Submit button
    submit_add = st.form_submit_button("➕ Save Student Record", use_container_width=True)

    if submit_add:
        # Call backend persistence API
        response: Dict[str, Any] = data_store.add_student(
            name=student_name,
            roll_number=roll_number,
            maths=maths_marks,
            science=science_marks,
            english=english_marks
        )

        # Handle HTTP Status Code returned by backend
        status_code = response.get("status_code", 500)
        message = response.get("message", "")

        if status_code == 201:
            st.success(f"**[HTTP 201 Created]** {message}")
            st.rerun()
        elif status_code == 400:
            st.error(f"**[HTTP 400 Bad Request]** {message}")
        else:
            st.error(f"**[HTTP {status_code} Error]** {message}")


# Sub-section 2.2: Delete Student (Stretch Goal)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🗑️ Delete Student Record")
with st.sidebar.expander("Manage / Remove Student", expanded=False):
    st.caption("Remove an existing student from the CSV persistence file.")

    # Fetch current student list to populate dropdown
    current_data_resp = data_store.get_all_students()
    current_df = current_data_resp.get("data", pd.DataFrame())

    if not current_df.empty:
        # Build options mapping: display string -> roll number
        options_dict = {
            f"Roll {row['Roll Number']} - {row['Name']}": str(row['Roll Number'])
            for _, row in current_df.iterrows()
        }
        selected_label = st.selectbox(
            "Select Student to Delete",
            options=list(options_dict.keys()),
            key="delete_student_select"
        )
        selected_roll = options_dict.get(selected_label, "")

        # Confirmation checkbox for safe deletion
        confirm_delete = st.checkbox("Confirm permanent deletion", key="confirm_delete_box")

        if st.button("Delete Selected Student", type="primary", use_container_width=True):
            if not confirm_delete:
                st.warning("Please check the confirmation box to proceed.")
            else:
                # Call backend delete API
                del_response = data_store.delete_student(selected_roll)
                del_status = del_response.get("status_code", 500)
                del_msg = del_response.get("message", "")

                if del_status == 200:
                    st.success(f"**[HTTP 200 OK]** {del_msg}")
                    st.rerun()
                elif del_status == 404:
                    st.error(f"**[HTTP 404 Not Found]** {del_msg}")
                else:
                    st.error(f"**[HTTP {del_status} Error]** {del_msg}")
    else:
        st.info("No students available to delete.")


# Sidebar info footer
st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Grading System Reference**\n"
    "- **A**: Average ≥ 90\n"
    "- **B**: 75 ≤ Average < 90\n"
    "- **C**: 60 ≤ Average < 75\n"
    "- **D**: 40 ≤ Average < 60\n"
    "- **F**: Average < 40 (Fail)"
)


# ==============================================================================
# SECTION 3: MAIN DASHBOARD HEADER & KPI SUMMARY
# ==============================================================================

# Header section
st.title("🎓 Student Marks Dashboard")
st.markdown(
    "Academic performance tracking, class analytics, and grade distribution management."
)

# Fetch latest data and analytics from the backend layer
students_response = data_store.get_all_students()
analytics_response = data_store.get_analytics()

df_students: pd.DataFrame = students_response.get("data", pd.DataFrame())
analytics: Dict[str, Any] = analytics_response.get("data", {})

total_students = analytics.get("total_students", 0)
class_avg = analytics.get("class_average", 0.0)
toppers = analytics.get("toppers", [])
subject_averages = analytics.get("subject_averages", {"Maths": 0.0, "Science": 0.0, "English": 0.0})
subject_pass_fail = analytics.get("subject_pass_fail", {})

# Top KPI Summary Cards (4 columns)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Enrolled</div>
        <div class="metric-value">{total_students}</div>
        <div class="metric-sub">Active students in database</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Class Average</div>
        <div class="metric-value">{class_avg}%</div>
        <div class="metric-sub">Across all 3 subjects</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    # Calculate overall passing rate (% of students with Average >= 40)
    overall_pass_pct = 0.0
    if total_students > 0 and not df_students.empty:
        pass_count = (df_students["Average"] >= 40.0).sum()
        overall_pass_pct = round((pass_count / total_students) * 100.0, 1)

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Overall Pass Rate</div>
        <div class="metric-value">{overall_pass_pct}%</div>
        <div class="metric-sub">Passing threshold ≥ 40%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    highest_score = toppers[0]["Total"] if toppers else 0.0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Highest Total</div>
        <div class="metric-value">{highest_score} <span style="font-size: 1rem; color: #64748b;">/ 300</span></div>
        <div class="metric-sub">Maximum marks achieved</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")


# ==============================================================================
# SECTION 4: HIGHLIGHTED CLASS TOPPER METRIC BOX
# ==============================================================================

if toppers:
    # If there are multiple toppers sharing the top total, display all cleanly
    topper_names = ", ".join([f"{t['Name']} (Roll: {t['Roll Number']})" for t in toppers])
    primary_topper = toppers[0]
    total_val = primary_topper.get("Total", 0.0)
    avg_val = primary_topper.get("Average", 0.0)
    grade_val = primary_topper.get("Grade", "A")

    st.markdown(f"""
    <div class="topper-card">
        <div class="topper-badge">🏆 Class Topper Distinction</div>
        <div class="topper-name">{topper_names}</div>
        <div style="color: #92400e; font-size: 0.95rem;">
            Outstanding academic excellence across Mathematics, Science, and English.
        </div>
        <div class="topper-stats">
            <div class="topper-stat-item">
                <div class="topper-stat-label">TOTAL MARKS</div>
                <div class="topper-stat-val">{total_val} / 300</div>
            </div>
            <div class="topper-stat-item">
                <div class="topper-stat-label">AVERAGE SCORE</div>
                <div class="topper-stat-val">{avg_val}%</div>
            </div>
            <div class="topper-stat-item">
                <div class="topper-stat-label">AWARDED GRADE</div>
                <div class="topper-stat-val">{grade_val}</div>
            </div>
            <div class="topper-stat-item">
                <div class="topper-stat-label">MATHS / SCI / ENG</div>
                <div class="topper-stat-val">
                    {primary_topper.get('Maths')} / {primary_topper.get('Science')} / {primary_topper.get('English')}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No student records available yet. Add students using the sidebar form.")


# ==============================================================================
# SECTION 5: DATA TABLE & CSV DOWNLOAD
# ==============================================================================

st.markdown('<div class="section-title">📋 Complete Student Marks Register</div>', unsafe_allow_html=True)

if not df_students.empty:
    # Quick search & filter bar
    col_search, col_filter, col_dl = st.columns([2, 1, 1])

    with col_search:
        search_query = st.text_input(
            "🔍 Search Student",
            placeholder="Search by student name or roll number...",
            label_visibility="collapsed"
        )

    with col_filter:
        grade_filter = st.selectbox(
            "Filter by Grade",
            options=["All Grades", "A", "B", "C", "D", "F"],
            label_visibility="collapsed"
        )

    # Apply search filter
    display_df = df_students.copy()
    if search_query.strip():
        q = search_query.strip().lower()
        display_df = display_df[
            display_df["Name"].str.lower().str.contains(q, na=False) |
            display_df["Roll Number"].astype(str).str.lower().str.contains(q, na=False)
        ]

    # Apply grade filter
    if grade_filter != "All Grades":
        display_df = display_df[display_df["Grade"] == grade_filter]

    # Convert DataFrame to CSV for the download button
    csv_export_data = display_df.to_csv(index=False).encode("utf-8")

    with col_dl:
        # Download button to save table as CSV
        st.download_button(
            label="📥 Download Table as CSV",
            data=csv_export_data,
            file_name="student_marks_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Interactive table rendering with formatted columns
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Roll Number": st.column_config.TextColumn("Roll No", width="small"),
            "Name": st.column_config.TextColumn("Student Name", width="medium"),
            "Maths": st.column_config.NumberColumn("Maths", format="%.1f"),
            "Science": st.column_config.NumberColumn("Science", format="%.1f"),
            "English": st.column_config.NumberColumn("English", format="%.1f"),
            "Total": st.column_config.NumberColumn("Total (/300)", format="%.1f"),
            "Average": st.column_config.ProgressColumn(
                "Average (%)",
                format="%.2f%%",
                min_value=0,
                max_value=100
            ),
            "Grade": st.column_config.TextColumn("Grade", width="small")
        }
    )
    st.caption(f"Showing {len(display_df)} of {total_students} registered students.")
else:
    st.warning("The student database is currently empty. Please add records using the sidebar.")


st.write("")
st.markdown("---")


# ==============================================================================
# SECTION 6: VISUALIZATIONS (BAR CHART & PASS/FAIL PIE CHARTS)
# ==============================================================================

st.markdown('<div class="section-title">📊 Visual Performance Analytics</div>', unsafe_allow_html=True)

if not df_students.empty:
    chart_col1, chart_col2 = st.columns([1, 1])

    # --------------------------------------------------------------------------
    # FEATURE 4: BAR CHART OF AVERAGE MARKS PER SUBJECT
    # --------------------------------------------------------------------------
    with chart_col1:
        st.subheader("📈 Average Marks by Subject")
        st.caption("Class-wide average score across Mathematics, Science, and English.")

        # Prepare subject averages DataFrame
        sub_avg_df = pd.DataFrame({
            "Subject": ["Maths", "Science", "English"],
            "Average Score": [
                subject_averages.get("Maths", 0.0),
                subject_averages.get("Science", 0.0),
                subject_averages.get("English", 0.0)
            ]
        })

        # Render styled bar chart using Streamlit native bar_chart
        st.bar_chart(
            sub_avg_df.set_index("Subject"),
            y="Average Score",
            color="#3b82f6",
            use_container_width=True
        )

        # Show detailed subject breakdown metrics below chart
        sub_c1, sub_c2, sub_c3 = st.columns(3)
        sub_c1.metric("📐 Maths Avg", f"{subject_averages.get('Maths', 0.0)}%")
        sub_c2.metric("🔬 Science Avg", f"{subject_averages.get('Science', 0.0)}%")
        sub_c3.metric("📖 English Avg", f"{subject_averages.get('English', 0.0)}%")

    # --------------------------------------------------------------------------
    # STRETCH GOAL: SUBJECT-WISE PASS / FAIL PIE CHART
    # --------------------------------------------------------------------------
    with chart_col2:
        st.subheader("🥧 Subject-wise Pass / Fail Breakdown")
        st.caption("Passing criteria: Score ≥ 40 (Grade D and above).")

        # Interactive subject selector for pie chart
        chosen_subject = st.radio(
            "Select Subject for Pass/Fail Analysis",
            options=["Maths", "Science", "English"],
            horizontal=True
        )

        # Extract pass / fail statistics for chosen subject
        subject_stats = subject_pass_fail.get(chosen_subject, {"pass": 0, "fail": 0, "pass_rate": 0.0})
        pass_count = subject_stats.get("pass", 0)
        fail_count = subject_stats.get("fail", 0)

        # Generate publication-quality Matplotlib pie chart
        fig, ax = plt.subplots(figsize=(4.5, 3.2), facecolor="none")

        if pass_count == 0 and fail_count == 0:
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", color="#64748b")
            ax.axis("off")
        else:
            slices = [pass_count, fail_count]
            labels = [f"Passed (≥40)\n{pass_count} students", f"Failed (<40)\n{fail_count} students"]
            # Clean emerald green for pass, soft crimson for fail
            colors = ["#10b981", "#ef4444"]

            # Only show explode on non-zero slices
            wedges, texts, autotexts = ax.pie(
                slices,
                labels=labels,
                autopct="%1.1f%%",
                startangle=140,
                colors=colors,
                wedgeprops={"edgecolor": "white", "linewidth": 2, "antialiased": True},
                textprops={"fontsize": 9, "color": "#1e293b"}
            )
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")
                autotext.set_fontsize(9)

            ax.axis("equal")  # Equal aspect ratio ensures circular pie

        st.pyplot(fig, use_container_width=False)

        # Quick summary badge
        pass_rate = subject_stats.get("pass_rate", 0.0)
        st.markdown(
            f"**{chosen_subject} Pass Rate:** `{pass_rate}%` ({pass_count} Passed, {fail_count} Failed)"
        )

else:
    st.info("Visual charts will appear once students are registered in the system.")


# ==============================================================================
# SECTION 7: ARCHITECTURE & BACKEND STATUS FOOTER
# ==============================================================================

st.markdown("---")
with st.expander("ℹ️ Architecture & System Information", expanded=False):
    st.markdown("""
    **Layered Architecture Overview:**
    - **Frontend Layer (`app.py`)**: Streamlit presentation and interactive components.
    - **Backend API & Controller (`data_store.py`)**: Request validation, grading logic, and HTTP status code responses (`200`, `201`, `400`, `404`).
    - **Persistence Layer (`students.csv`)**: File storage abstracted via pandas DataFrame operations.
    
    *Note: The persistence layer can easily be replaced by an SQLite database without requiring any changes to `app.py`.*
    """)
