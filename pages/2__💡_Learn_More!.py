import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_image_comparison import image_comparison

st.set_page_config(page_title="RollShift AI - Film Processing", layout="wide")

st.title('🎞️ RollShift AI - Film Processing Explained ✨')
st.write("Explore the advanced techniques used in **RollShift AI**. 🚀")

st.markdown("---")

st.subheader("Film Processing - Before & After 📷")

negative_path = "/workspaces/RollShift/media/samples/phoenix_sample_neg.jpg"
positive_path = "/workspaces/RollShift/media/samples/phoenix_sample_positive.jpg"

negative_image = Image.open(negative_path)
positive_image = Image.open(positive_path)

# Before-After Image Comparison
st.write("🔄 Drag to compare:")
image_comparison(img1=negative_image, img2=positive_image, label1="Raw Negative", label2="RollShift-Processed")

st.markdown("---")

st.header("🛠️ How RollShift AI Converts Film Negatives")

with st.expander("🔄 **1. Color Inversion & Base Color Removal**"):
    st.write("""
    - **Why?** Film negatives store images in reverse colors, so they need to be inverted.
    - **How?** We detect the base color of the negative using the **99th percentile of brightness** and adjust the image accordingly.
    """)

with st.expander("🎛️ **2. Grey World Assumption for Color Balancing**"):
    st.write("""
    - **Why?** Film negatives often have strong color casts.
    - **How?** We assume the average color in an image should be **neutral gray** and balance the color channels accordingly.
    """)

with st.expander("🌟 **3. Gamma Correction for Proper Exposure**"):
    st.write("""
    - **Why?** Film scans often appear too dark or too bright.
    - **How?** We apply **gamma correction (default 0.5)** to adjust brightness and contrast dynamically.
    """)

with st.expander("🎨 **4. RGB Channel Adjustments for Fine-Tuning**"):
    st.write("""
    - **Why?** Some film stocks require fine-tuned adjustments to match their original look.
    - **How?** Users can manually adjust **Red, Green, and Blue (RGB) levels** to refine the output.
    """)

st.markdown("---")

st.header("Pushing & Pulling Film 🧪")

with st.expander("📌 What is Pushing & Pulling Film?"):
    st.write("""
    - **Pushing Film:** When you rate your film at a higher ISO than its box speed and develop it for a longer time to compensate. This increases contrast and grain.
    - **Pulling Film:** When you rate your film at a lower ISO and develop it for a shorter time, resulting in lower contrast and finer grain.
    - **Why?** Pushing is often used in low-light conditions to brighten images, while pulling helps control highlights in high-contrast scenes.
    """)

st.markdown("---")

st.header("🎛️ Try It Yourself!")

st.write("Ready to experiment? Click below to **test film conversion interactively**!")

if st.button("🔬 Experiment with Film Conversion!"):
    st.switch_page("1__🎞️_Film_Converting.py")

st.markdown("---")


st.markdown("🔗 **[RollShift AI GitHub Repo](https://github.com/3li-dev/RollShift)**")
