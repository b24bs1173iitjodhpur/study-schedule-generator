import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

st.title("Smart Study Schedule Generator")

# Step 1: Input form for subjects, difficulty, and hours
st.header("Step 1: Enter your subjects and available study hours")

num_subjects = st.number_input("How many subjects do you want to schedule?", min_value=1, max_value=20, value=3)

subjects_data = []
for i in range(num_subjects):
    col1, col2 = st.columns([2,1])
    with col1:
        subject = st.text_input(f"Subject #{i+1} Name", key=f"subj_name_{i}")
    with col2:
        difficulty = st.slider(f"Difficulty for {subject if subject else 'Subject'} (1=easy, 5=hard)", 1,5,3, key=f"diff_{i}")
    subjects_data.append({"subject": subject, "difficulty": difficulty})

available_hours = st.number_input("Total available study hours per week", min_value=1, max_value=100, value=15)

# Validate inputs
if st.button("Generate Schedule"):

    # Filter out empty subjects
    subjects_data = [s for s in subjects_data if s['subject'].strip() != ""]
    if not subjects_data:
        st.error("Please enter at least one subject name.")
        st.stop()

    # Simple weighting by difficulty
    total_difficulty = sum(s['difficulty'] for s in subjects_data)
    if total_difficulty == 0:
        total_difficulty = 1  # avoid division by zero

    # Calculate hours per subject proportionally by difficulty
    for s in subjects_data:
        s['allocated_hours'] = round((s['difficulty']/total_difficulty)*available_hours, 1)

    # Create DataFrame for display
    df_schedule = pd.DataFrame(subjects_data)[["subject", "difficulty", "allocated_hours"]]
    df_schedule.columns = ["Subject", "Difficulty (1-5)", "Allocated Hours per Week"]

    st.subheader("Your Weekly Study Schedule")
    st.table(df_schedule)

    # Step 3: PDF export button
    def generate_pdf(dataframe):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height-72, "Smart Study Schedule")
        c.setFont("Helvetica", 12)

        y = height - 100
        for i, row in dataframe.iterrows():
            line = f"{row['Subject']}: Difficulty {row['Difficulty (1-5)']}, Hours: {row['Allocated Hours per Week']}"
            c.drawString(72, y, line)
            y -= 20
            if y < 72:
                c.showPage()
                y = height - 72

        c.save()
        buffer.seek(0)
        return buffer

    pdf_buffer = generate_pdf(df_schedule)

    st.download_button(
        label="Download Schedule as PDF",
        data=pdf_buffer,
        file_name="study_schedule.pdf",
        mime="application/pdf"
    )
