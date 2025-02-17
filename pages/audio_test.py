
import streamlit as st
import base64

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">  <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

# Example usage (replace with your audio file path):
audio_file = "/workspaces/RollShift/agitation_beep.mp3"  # Make sure the path is correct!
autoplay_audio(audio_file)

# Rest of your Streamlit app code...
st.write("Your Streamlit app content goes here.")
st.write("# Auto-playing Audio!")

autoplay_audio("agitation_beep.mp3")