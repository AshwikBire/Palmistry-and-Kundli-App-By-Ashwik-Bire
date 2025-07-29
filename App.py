# kundli_app_generator.py
app_code = '''
import streamlit as st
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from fpdf import FPDF
import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
from streamlit_option_menu import option_menu

st.set_page_config(page_title="कुंडली और हस्तरेखा", layout="wide")

st.markdown("<h1 style='text-align: center; color: gold;'>🔮 कुंडली और हस्तरेखा विश्लेषण</h1>", unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=["🏠 होम", "🔭 कुंडली", "🧪 दोष", "✋ हस्तरेखा", "📄 PDF"],
    icons=["house", "stars", "exclamation", "hand-index", "file-earmark-pdf"],
    orientation="horizontal"
)

def generate_kundli(date, time, place):
    dt = Datetime(date, time, '+05:30')  # भारत का समय
    pos = GeoPos("19.8762", "75.3433")  # औरंगाबाद (स्थिर), आवश्यकता अनुसार बदलें
    chart = Chart(dt, pos)
    return chart

def check_dosh(chart):
    dosh_list = []
    if chart.get('MARS').sign == chart.get('ASC').sign:
        dosh_list.append("मंगल दोष")
    return dosh_list

def create_pdf(name, dosh_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt=f"कुंडली रिपोर्ट: {name}", ln=True, align='C')
    pdf.ln(10)
    for dosh in dosh_list:
        pdf.cell(200, 10, txt=f"- {dosh}", ln=True)
    pdf.ln(20)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Powered by Ashwik Bire", align='C')
    return pdf.output(dest='S').encode('latin1')

def scan_hand(image):
    mp_hands = mp.solutions.hands
    with mp_hands.Hands(static_image_mode=True, max_num_hands=1) as hands:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hands.process(image_rgb)
        if result.multi_hand_landmarks:
            return "हस्तरेखा डिटेक्ट हुई"
        else:
            return "हस्तरेखा नहीं मिली"

if selected == "🏠 होम":
    st.markdown("स्वागत है आपकी व्यक्तिगत ज्योतिष सहायक में।")
elif selected == "🔭 कुंडली":
    name = st.text_input("नाम")
    date = st.date_input("जन्म तिथि")
    time = st.time_input("समय")
    if st.button("कुंडली बनाएँ"):
        chart = generate_kundli(str(date), str(time)[:5], "भारत")
        st.success("कुंडली तैयार है।")
elif selected == "🧪 दोष":
    name = st.text_input("नाम (दोष चेक के लिए)")
    date = st.date_input("जन्म तिथि")
    time = st.time_input("समय")
    if st.button("दोष चेक करें"):
        chart = generate_kundli(str(date), str(time)[:5], "भारत")
        dosh = check_dosh(chart)
        if dosh:
            st.error("दोष पाए गए:")
            for d in dosh:
                st.write(f"- {d}")
        else:
            st.success("कोई दोष नहीं पाया गया।")
elif selected == "✋ हस्तरेखा":
    uploaded = st.file_uploader("अपनी हथेली की तस्वीर अपलोड करें", type=["jpg", "png"])
    if uploaded:
        img = cv2.imdecode(np.frombuffer(uploaded.read(), np.uint8), 1)
        result = scan_hand(img)
        st.success(result)
elif selected == "📄 PDF":
    name = st.text_input("नाम (PDF के लिए)")
    dosh_sample = ["मंगल दोष", "कालसर्प दोष"]
    if st.button("PDF डाउनलोड करें"):
        pdf_bytes = create_pdf(name, dosh_sample)
        st.download_button("यहाँ क्लिक करें PDF डाउनलोड के लिए", data=pdf_bytes, file_name="kundli_report.pdf")

