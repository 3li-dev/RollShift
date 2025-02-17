import streamlit as st
import time
import base64
from datetime import timedelta

# Function to play audio in Streamlit using base64 encoding
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

# Function to run the timer with agitation alerts
def run_timer(step_name, duration, agitation_interval=60, agitation_duration=10):
    st.subheader(f"{step_name} - {str(timedelta(seconds=duration))}")
    
    start_time = time.time()
    end_time = start_time + duration

    time_display = st.empty()  # Container for updating time remaining
    agitation_alert = st.empty()  # Container for showing/hiding agitation alerts

    last_displayed_time = -1  # Prevents redundant updates

    while time.time() < end_time:
        elapsed = int(time.time() - start_time)
        remaining = int(end_time - time.time())

        # Update the displayed remaining time only once per second
        if remaining != last_displayed_time:
            time_display.metric(label="Time Remaining", value=str(timedelta(seconds=remaining)))
            last_displayed_time = remaining

        # Trigger agitation at specified intervals
        if elapsed % agitation_interval == 0 and elapsed != 0:
            agitation_alert.warning(f"Agitate Now! ({elapsed // agitation_interval} agitation(s) done)")
            
            # Play beep continuously for the agitation duration
            for _ in range(agitation_duration):
                autoplay_audio("agitation_beep.mp3")  
                time.sleep(1)  # Ensure the sound plays for 10 seconds

            agitation_alert.empty()  # Remove the agitation alert after 10 seconds

        time.sleep(1)  # Sleep for 1 second before the next iteration

    st.success(f"{step_name} Complete!")

# Streamlit UI
st.title("CineStill CS41 Film Development Assistant")

# Input for temperature
temperature = st.number_input("Enter your chemical temperature (°C)", min_value=30.0, max_value=40.0, value=39.0, step=0.1)

# Start development process
if st.button("Start Development Process"):
    st.info("Step 1: Pre-Soak for 1 minute")
    run_timer("Pre-Soak", 60)

    st.info("Step 2: Color Developer")
    dev_time = 210  # Example development time, adjust as needed
    run_timer("Color Developer", dev_time, agitation_interval=30, agitation_duration=10)

    st.info("Step 3: Blix (Bleach + Fix)")
    run_timer("Blix", 480, agitation_interval=30, agitation_duration=10)

    st.info("Step 4: Final Rinse")
    run_timer("Final Rinse", 180, agitation_interval=0)  # No agitation needed

    st.success("Film Development Complete! Dry your film and enjoy your negatives.")
