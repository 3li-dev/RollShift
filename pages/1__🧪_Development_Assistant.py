import streamlit as st
import time
import base64
from datetime import timedelta
import uuid

# Function to autoplay audio
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">  
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Function to run a timer with agitation alerts
def run_timer(step_name, duration, agitation_interval=60, agitation_duration=10):
    st.markdown(f"<h2 style='text-align: center;'>{step_name} - {timedelta(seconds=duration)}</h2>", unsafe_allow_html=True)
    
    start_time = time.time()
    end_time = start_time + duration
    
    time_display = st.empty()
    agitation_alert = st.empty()
    
    last_displayed_time = None
    
    while time.time() < end_time:
        elapsed = int(time.time() - start_time)
        remaining = int(end_time - time.time())
        
        if remaining != last_displayed_time:
            time_display.markdown(f"<h3 style='text-align: center;'>⏳ Time Remaining: {timedelta(seconds=remaining)}</h3>", unsafe_allow_html=True)
            last_displayed_time = remaining
        
        if agitation_interval > 0 and elapsed % agitation_interval == 0 and elapsed > 0:
            agitation_alert.warning(f"⚠️ Agitate Now! ({elapsed // agitation_interval} agitation(s) done)")
            autoplay_audio("agitation.mp3")  # Play sound
            
            # Non-blocking wait for agitation duration
            agitation_end = time.time() + agitation_duration
            while time.time() < agitation_end:
                time_display.markdown(f"<h3 style='text-align: center;'>⏳ Time Remaining: {timedelta(seconds=int(end_time - time.time()))}</h3>", unsafe_allow_html=True)
                time.sleep(1)
            
            agitation_alert.empty()
        
        time.sleep(1)
    
    st.success(f"✅ {step_name} Complete!")
    st.session_state.step_index += 1
    st.rerun()

# Streamlit UI Setup
st.title("Film Development Assistant 🧪")

# Select Chemistry Process
st.selectbox("Select your chemistry process", ["CineStill C-41 Two Bath Process"])

# Temperature Input
temperature = st.number_input("Enter your chemical's temperature (°C)", 30.0, 40.0, 39.0, 0.1)

# Film Development Steps
steps = [
    ("Pre-Soak", 60),
    ("Color Developer", 210, 30, 10),
    ("Blix (Bleach + Fix)", 480, 30, 10),
    ("Final Rinse", 180, 0, 0)
]

if "step_index" not in st.session_state or st.session_state.step_index is None:
    st.session_state.step_index = None

if st.session_state.step_index is None:
    if st.button("▶️ Start Development Process", use_container_width=True):
        st.session_state.step_index = 0
        st.rerun()
elif st.session_state.step_index < len(steps):
    step = steps[st.session_state.step_index]
    st.info(f"🔹 Step {st.session_state.step_index + 1}: {step[0]}")
    
    if "step_running" not in st.session_state:
        st.session_state.step_running = False
    
    if not st.session_state.step_running:
        if st.button("▶️ Start Step", use_container_width=True):
            st.session_state.step_running = True
            agitation_values = (60, 10) if len(step) < 4 else step[2:]
            run_timer(step[0], step[1], *agitation_values)
    
    if st.session_state.step_running:
        if st.button("⏭️ Skip Step", use_container_width=True):
            st.session_state.step_index += 1
            st.session_state.step_running = False
            st.rerun()
else:
    st.success("🎉 Film Development Complete! Dry your film and enjoy your negatives.")
