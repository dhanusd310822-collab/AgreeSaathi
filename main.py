import json
import streamlit as st
import random
from datetime import datetime, timedelta
from streamlit_mic_recorder import speech_to_text

# 1. Page Configuration
st.set_page_config(page_title="AgriSaathi - Voice & App", page_icon="", layout="wide")

# 2. Localization Dictionary (No Emojis)
LANG_DICT = {
    "English": {
        "title": "AgriSaathi: Voice-First Agricultural Assistant",
        "subtitle": "LEAP Agritech Hackathon 2026 | Team Silicon",
        "tab1": "1. Profile & Voice",
        "tab2": "2. Schemes",
        "tab3": "3. AI Assistant",
        "tab4": "4. Claims & 72Hr Timer",
        "p_header": "Farmer Profile & Voice Input",
        "details_header": "Farmer Profile Details",
        "name_label": "Farmer Name:",
        "land_label": "Land Area (Acres):",
        "crop_label": "Crop Type:",
        "dist_label": "District (Karnataka):",
        "save_btn": "Save Profile & Find Schemes",
        "schemes_header": "Eligible Central & State Schemes",
        "apply_btn": "Apply Now",
        "ai_header": "Multilingual AI Assistant",
        "claim_header": "Crop Loss Claim Filing & 72-Hour Deadline Tracker",
        "policy_label": "Insurance Policy Number / FRUITS ID:",
        "survey_label": "Land Survey Number / RTC Plot ID:",
        "calamity_label": "Calamity Type:",
        "photo_label": "Upload Geotagged Damage Photo:",
        "claim_btn": "Submit 72-Hour Claim Intimation",
        "tracker_header": "Live Claim Pipeline & WhatsApp/SMS Notification Simulator"
    },
    "ಕನ್ನಡ (Kannada)": {
        "title": "ಅಗ್ರಿಸಾಥಿ: ಧ್ವನಿ-ಮೊದಲ ಕೃಷಿ ಸಹಾಯಕ",
        "subtitle": "LEAP ಅಗ್ರಿಟೆಕ್ ಹ್ಯಾಕಥಾನ್ 2026 | ತಂಡ ಸಿಲಿಕಾನ್",
        "tab1": "1. ಪ್ರೊಫೈಲ್ ಮತ್ತು ಧ್ವನಿ",
        "tab2": "2. ಯೋಜನೆಗಳು",
        "tab3": "3. AI ಸಹಾಯಕ",
        "tab4": "4. ಹಕ್ಕುಗಳು ಮತ್ತು 72 ಗಂಟೆಗಳ ಟೈಮರ್",
        "p_header": "ರೈತ ಪ್ರೊಫೈಲ್ ಮತ್ತು ಧ್ವನಿ ಇನ್‌ಪುಟ್",
        "details_header": "ರೈತ ಪ್ರೊಫೈಲ್ ವಿವರಗಳು",
        "name_label": "ರೈತನ ಹೆಸರು:",
        "land_label": "ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ (ಎಕರೆಗಳಲ್ಲಿ):",
        "crop_label": "ಬೆಳೆಯ ಪ್ರಕಾರ:",
        "dist_label": "ಜಿಲ್ಲೆ (ಕರ್ನಾಟಕ):",
        "save_btn": "ಪ್ರೊಫೈಲ್ ಉಳಿಸಿ ಮತ್ತು ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಿ",
        "schemes_header": "ಅರ್ಹ ಕೇಂದ್ರ ಮತ್ತು ರಾಜ್ಯ ಯೋಜನೆಗಳು",
        "apply_btn": "ಈಗ ಅರ್ಜಿ ಹಾಕಿ",
        "ai_header": "ಬಹುಭಾಷಾ AI ಸಹಾಯಕ",
        "claim_header": "ಬೆಳೆ ಹಾನಿ ಪರಿಹಾರ ಅರ್ಜಿ ಮತ್ತು 72 ಗಂಟೆಗಳ ಗಡುವು ಟ್ರ್ಯಾಕರ್",
        "policy_label": "ವಿಮಾ ಪಾಲಿಸಿ ಸಂಖ್ಯೆ / FRUITS ID:",
        "survey_label": "ಸರ್ವೆ ಸಂಖ್ಯೆ / RTC ಪ್ಲಾಟ್ ID:",
        "calamity_label": "ವಿಪತ್ತಿನ ಪ್ರಕಾರ:",
        "photo_label": "ಜಿಯೋಟ್ಯಾಗ್ ಮಾಡಲಾದ ಹಾನಿಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ:",
        "claim_btn": "72 ಗಂಟೆಗಳ ಒಳಗೆ ಹಾನಿ ವರದಿ ಸಲ್ಲಿಸಿ",
        "tracker_header": "ಲೈವ್ ಕ್ಲೈಮ್ ಮತ್ತು WhatsApp/SMS ಅಧಿಸೂಚನೆ ಸಿಮ್ಯುಲೇಟರ್"
    }
}

# 3. Sidebar Language & Twilio Simulation Controls
st.sidebar.title("Language / ಭಾಷೆ")
selected_lang = st.sidebar.selectbox("Choose Language:", ["English", "ಕನ್ನಡ (Kannada)"])
t = LANG_DICT[selected_lang]
lang_code = "kn" if selected_lang == "ಕನ್ನಡ (Kannada)" else "en"

st.sidebar.markdown("---")
st.sidebar.markdown("Twilio API Gateway status:")
st.sidebar.success("Connected (Twilio SMS/WhatsApp Active)")

# 4. Load schemes
@st.cache_data
def load_schemes():
    try:
        with open("schemes.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [
            {
                "id": 1,
                "name_en": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "name_kn": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ",
                "category": "Crop Insurance",
                "required_documents": ["Aadhaar", "Land RTC", "Bank Passbook"]
            }
        ]

SCHEMES_DB = load_schemes()

# 5. Session State Initialization
if "applications" not in st.session_state:
    st.session_state["applications"] = []
if "claims" not in st.session_state:
    st.session_state["claims"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "Namaskara! Ask me anything about government schemes or crop insurance."}
    ]
if "farmer_name_val" not in st.session_state:
    st.session_state["farmer_name_val"] = "Ramesh Kumar" if lang_code == "en" else "ರಮೇಶ್ ಕುಮಾರ್"
if "incident_time" not in st.session_state:
    st.session_state["incident_time"] = datetime.now() - timedelta(hours=12)

# 6. Define Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    t["tab1"], 
    t["tab2"], 
    t["tab3"], 
    t["tab4"]
])

# ==========================================
# TAB 1: PROFILE & VOICE INPUT
# ==========================================
with tab1:
    st.header(t["p_header"])
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown(f"Live Voice Input ({selected_lang})")
        spoken_text = speech_to_text(
            language=f"{lang_code}-IN",
            start_prompt="Start Speaking",
            stop_prompt="Stop & Transcribe",
            key='profile_mic'
        )
        if spoken_text:
            st.session_state["farmer_name_val"] = spoken_text
            st.success(f"Captured Voice: {spoken_text}")
            
    with col_v2:
        st.markdown("Demo Backup:")
        if st.button("Simulate Voice Input"):
            st.session_state["farmer_name_val"] = "Ramesh Kumar" if lang_code == "en" else "ರಮೇಶ್ ಕುಮಾರ್"
            st.success("Voice simulated successfully")

    st.markdown("---")
    st.subheader(t["details_header"])
    
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            farmer_name = st.text_input(t["name_label"], value=st.session_state["farmer_name_val"])
            land_acres = st.number_input(t["land_label"], min_value=0.1, value=3.5, step=0.5)
            crop_type = st.selectbox(t["crop_label"], ["Paddy / ಭತ್ತ", "Sugarcane / ಕಬ್ಬು", "Ragi / ರಾಗಿ"])
        with c2:
            district = st.selectbox(t["dist_label"], ["Mandya / ಮಂಡ್ಯ", "Mysuru / ಮೈಸೂರು", "Hassan / ಹಾಸನ"])
         
        save_profile = st.form_submit_button(t["save_btn"])
        
    if save_profile:
        st.session_state["profile"] = {"name": farmer_name, "acres": land_acres, "district": district}
        st.success("Profile saved successfully. Check Tab 2.")

# ==========================================
# TAB 2: SCHEMES
# ==========================================
with tab2:
    st.header(t["schemes_header"])
    for scheme in SCHEMES_DB:
        with st.container():
            display_name = scheme['name_en'] if lang_code == "en" else scheme['name_kn']
            st.subheader(display_name)
            st.write(f"Required Documents: {', '.join(scheme['required_documents'])}")
            if st.button(t["apply_btn"], key=f"apply_{scheme['id']}"):
                st.success(f"Applied successfully for {display_name}")
            st.divider()

# ==========================================
# TAB 3: AI ASSISTANT
# ==========================================
with tab3:
    st.header(t["ai_header"])
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
    user_prompt = st.chat_input("Type your question here...")
    if user_prompt:
        st.session_state["chat_history"].append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)
        bot_response = "Under PMFBY guidelines, crop loss intimation due to localized calamities must be reported within 72 hours."
        st.session_state["chat_history"].append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.write(bot_response)

# ==========================================
# TAB 4: CLAIMS & 72-HOUR DEADLINE TIMER
# ==========================================
with tab4:
    st.header(t["claim_header"])
    
    # 72-HOUR DEADLINE TIMER WIDGET
    st.markdown("### PMFBY Mandate: 72-Hour Loss Intimation Countdown")
    
    deadline = st.session_state["incident_time"] + timedelta(hours=72)
    now = datetime.now()
    remaining = deadline - now
    
    if remaining.total_seconds() > 0:
        hours_left = int(remaining.total_seconds() // 3600)
        minutes_left = int((remaining.total_seconds() % 3600) // 60)
        
        col_timer1, col_timer2 = st.columns([2, 1])
        with col_timer1:
            st.warning(f"URGENT DEADLINE WARNING: You have {hours_left} hours and {minutes_left} minutes left to report crop loss and secure your insurance claim under PMFBY guidelines.")
        with col_timer2:
            if st.button("Reset Incident Time (Demo)"):
                st.session_state["incident_time"] = datetime.now()
                st.rerun()
    else:
        st.error("DEADLINE EXPIRED: The mandatory 72-hour window for reporting crop loss has passed.")

    st.markdown("---")
    
    with st.form("claim_form"):
        c1, c2 = st.columns(2)
        with c1:
            policy_no = st.text_input(t["policy_label"], "POL-PMFBY-94821")
            survey_no = st.text_input(t["survey_label"], "Sy. No. 112/4")
        with c2:
            disaster_type = st.selectbox(t["calamity_label"], ["Inundation / Heavy Rains", "Hailstorm", "Cloudburst"])
            damage_photo = st.file_uploader(t["photo_label"], type=["jpg", "png", "jpeg"])
        sub_claim = st.form_submit_button(t["claim_btn"])
        
    if sub_claim:
        claim_id = f"CLM-{random.randint(10000, 99999)}"
        st.session_state["claims"].append({"id": claim_id, "survey": survey_no, "status": "Submitted"})
        st.success(f"Claim successfully submitted within the 72-hour window. Claim ID: {claim_id}")
        
        st.markdown("### Twilio API Gateway: Notification Triggered")
        st.info(f"""
        [WhatsApp / SMS Simulation Sent to +91 98765 43210]:  
        “Dear Ramesh Kumar, your crop loss intimation for Survey No. 112/4 has been successfully registered via AgriSaathi. Claim ID: {claim_id}. Status: Under Field Verification.”
        """)
        
    st.markdown("---")
    st.subheader(t["tracker_header"])
    if not st.session_state["claims"]:
        st.info("No active claims filed yet.")
    else:
        for clm in st.session_state["claims"]:
            st.write(f"Claim ID: {clm['id']} | Survey: {clm['survey']} | Status: {clm['status']}")

# ==========================================
# TAB 4: CLAIMS & 72-HOUR DEADLINE TIMER
# ==========================================
with tab4:
    st.header(t["claim_header"])
    
    st.markdown("### PMFBY Mandate: 72-Hour Loss Intimation Countdown")
    
    deadline = st.session_state["incident_time"] + timedelta(hours=72)
    now = datetime.now()
    remaining = deadline - now
    
    if remaining.total_seconds() > 0:
        hours_left = int(remaining.total_seconds() // 3600)
        minutes_left = int((remaining.total_seconds() % 3600) // 60)
        
        col_timer1, col_timer2 = st.columns([2, 1])
        with col_timer1:
            st.warning(f"URGENT DEADLINE WARNING: You have {hours_left} hours and {minutes_left} minutes left to report crop loss and secure your insurance claim under PMFBY guidelines.")
        with col_timer2:
            # FIXED RESET BUTTON
            if st.button("Reset Incident Time Demo"):
                st.session_state["incident_time"] = datetime.now()
                st.rerun()
    else:
        st.error("DEADLINE EXPIRED: The mandatory 72-hour window for reporting crop loss has passed.")
        if st.button("Reset Expired Timer"):
            st.session_state["incident_time"] = datetime.now()
            st.rerun()
