import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

CSV_FILE = "workout_logs.csv"

def load_data():
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Activity", "Metric", "Value"])
    return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def plot_activity(df, activity):
    plt.figure(figsize=(6, 4))
    activity_df = df[df["Activity"].str.lower() == activity.lower()]
    activity_df["Date"] = pd.to_datetime(activity_df["Date"], errors="coerce")
    activity_df = activity_df.sort_values("Date")
    plt.plot(activity_df["Date"], activity_df["Value"], marker="o")
    plt.title(f"{activity} Progress")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.grid(True)
    
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf

def generate_pdf(df, plot_buffer):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Fitness Progress Report 💪", styles["Title"]))
    story.append(Spacer(1, 12))

    # Table data
    for _, row in df.iterrows():
        story.append(Paragraph(f"{row['Date']} - {row['Activity']} - {row['Metric']}: {row['Value']}", styles["Normal"]))

    story.append(Spacer(1, 24))
    
    # Add the plot
    img = Image(plot_buffer, width=5*inch, height=3*inch)
    story.append(img)

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer

def main():
    st.title("Fitness Progress Tracker 💪")

    # Load data
    df = load_data()

    # Form to add workout log
    st.subheader("Add a New Workout Log")
    with st.form("log_form"):
        date = st.date_input("Date", datetime.today())
        activity = st.text_input("Activity")
        metric = st.text_input("Metric (e.g., Distance, Reps, Weight)")
        value = st.number_input("Value", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Add Log")

        if submitted:
            new_entry = pd.DataFrame([[date, activity, metric, value]], columns=df.columns)
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            st.success("Log submitted successfully!")

    st.subheader("Your Progress Dashboard")

    if not df.empty:
        # Select activity
        activities = sorted(df["Activity"].dropna().unique())
        selected_activity = st.selectbox("Select Activity to Plot", activities)

        if selected_activity:
            plot_buf = plot_activity(df, selected_activity)
            st.image(plot_buf)

            # Download button for PDF
            pdf_buf = generate_pdf(df, plot_buf)
            st.download_button(
                label="📥 Download All Logs + Plot as PDF",
                data=pdf_buf,
                file_name="fitness_report.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
