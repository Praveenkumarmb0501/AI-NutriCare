import streamlit as st
import json
# Import your custom modules (ensure these files are in the same folder)
from data_extractor import MedicalReportExtractor
from health_analyzer import HealthAnalyzer
from diet_generator import DietPlanGeneratorfrom database import init_db, save_record, get_all_records

# Initialize the database when the app starts
init_db()

# Initialize the modules
@st.cache_resource
def load_modules():
    extractor = MedicalReportExtractor()
    analyzer = HealthAnalyzer() # Make sure you have your trained .pkl file
    generator = DietPlanGenerator()
    return extractor, analyzer, generator

extractor, analyzer, generator = load_modules()

# --- UI Setup ---
st.set_page_config(page_title="AI-NutriCare", layout="wide")
st.title("🍏 AI-NutriCare: Personalized Diet Plan Generator")
st.markdown("Upload your medical report to get AI-driven health insights and a customized diet plan.")
# --- Sidebar: Patient History ---
st.sidebar.title("🗂️ Patient History")
st.sidebar.markdown("View previously generated diet plans.")

history_records = get_all_records()
if not history_records:
    st.sidebar.info("No past records found.")
else:
    for record in history_records:
        record_id, timestamp, name, condition, risk, plan_json_str = record
        with st.sidebar.expander(f"{name} - {timestamp[:10]}"):
            st.write(f"**Condition:** {condition}")
            st.write(f"**Risk:** {risk}%")

            # Add a button to let them re-download past plans
            st.download_button(
                label="📥 Download JSON",
                data=plan_json_str,
                file_name=f"{name.replace(' ', '_')}_diet_plan.json",
                mime="application/json",
                key=f"download_{record_id}" # Unique key for Streamlit buttons
            )  
# --- File Uploader ---
uploaded_file = st.file_uploader("Upload Medical Report (PDF/Image)", type=["pdf", "jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.info("File uploaded successfully. Processing...")
    
    # Save the uploaded file temporarily so our extractor can read it
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    # --- Execute Pipeline ---
    with st.spinner('Extracting medical data (Phase 1)...'):
        extracted_data = extractor.process_document(temp_path)
        
    with st.spinner('Analyzing health risks via ML (Phase 2)...'):
        # For testing, you might need to mock this if your ML model isn't fully tuned yet
        ml_diagnosis = analyzer.predict_diabetes_risk(extracted_data)
        
    with st.spinner('Generating personalized diet plan (Phase 3)...'):
        diet_plan = generator.generate_plan(extracted_data, ml_diagnosis)

    # --- Display Results ---
    st.success("Analysis Complete!")
    
    # Use columns to create a dashboard layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Extracted Health Metrics")
        # Display abnormal findings nicely
        abnormal = extracted_data.get("abnormal_findings", [])
        if abnormal:
            for item in abnormal:
                st.error(f"**{item['canonical_test_key'].replace('_', ' ').title()}**: {item['observed_value']} (Severity: {item['severity']})")
        else:
            st.success("No abnormal metrics detected.")
            
        st.subheader("🩺 ML Diagnosis")
        st.warning(f"Detected Condition Risk: **{ml_diagnosis['condition']}**")
        st.write(f"Risk Probability: {ml_diagnosis['risk_probability']}%")

    with col2:
        st.subheader("🍽️ Your Personalized Diet Plan")
        st.info(diet_plan.get("patient_summary", "Diet plan optimized for your health metrics."))
        
        # Display Day 1
        st.markdown("### Day 1")
        day_1 = diet_plan.get("diet_plan", {}).get("day_1", {})
        st.write(f"**Breakfast:** {day_1.get('breakfast', 'N/A')}")
        st.write(f"**Lunch:** {day_1.get('lunch', 'N/A')}")
        st.write(f"**Snack:** {day_1.get('snack', 'N/A')}")
        st.write(f"**Dinner:** {day_1.get('dinner', 'N/A')}")
        
        # Display Day 2
        st.markdown("### Day 2")
        day_2 = diet_plan.get("diet_plan", {}).get("day_2", {})
        st.write(f"**Breakfast:** {day_2.get('breakfast', 'N/A')}")
        st.write(f"**Lunch:** {day_2.get('lunch', 'N/A')}")
        st.write(f"**Snack:** {day_2.get('snack', 'N/A')}")
        st.write(f"**Dinner:** {day_2.get('dinner', 'N/A')}")
        # --- Execute Pipeline ---
    try:
        with st.spinner('Extracting medical data via Vision LLM (Phase 1)...'):
            extracted_data = extractor.process_document(temp_path)
            
        with st.spinner('Analyzing health risks via XGBoost (Phase 2)...'):
            ml_diagnosis = analyzer.predict_diabetes_risk(extracted_data)
            
        with st.spinner('Generating personalized diet plan via NLP (Phase 3)...'):
            # This is the line you are looking for!
            diet_plan = generator.generate_plan(extracted_data, ml_diagnosis)
            
            # --- PASTE THE NEW DATABASE LOGIC RIGHT HERE ---
            # Extract a patient name if available, otherwise use a default
            patient_info = extracted_data.get("patient_information", {})
            patient_name = patient_info.get("patient_name", "Unknown Patient")
            
            # Save the generated plan to SQLite
            save_record(
                patient_name=patient_name,
                condition=ml_diagnosis.get('condition', 'Unknown'),
                risk=ml_diagnosis.get('risk_probability', 0),
                diet_plan=diet_plan
            )
            # -----------------------------------------------

        # --- Display Results ---
        st.success("Analysis Complete!")
    # --- Export Button ---
    st.markdown("---")
    st.download_button(
        label="📥 Download Diet Plan as JSON",
        data=json.dumps(diet_plan, indent=2),
        file_name="personalized_diet_plan.json",
        mime="application/json"
    )