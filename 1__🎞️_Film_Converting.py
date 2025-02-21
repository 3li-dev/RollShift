import streamlit as st
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from streamlit_image_comparison import image_comparison

# Function to find base color using the 99th percentile of brightness
def find_base(neg):
    flat_img = neg.reshape(-1, 3)
    brightness = np.sum(flat_img, axis=1)
    idx = np.argsort(brightness)[-int(0.01 * len(brightness)):]  # Top 1% brightest pixels
    white_sample = np.mean(flat_img[idx], axis=0)
    return white_sample

# Function to invert the negative image with enhanced color balancing
def invert(neg, base):
    b, g, r = cv2.split(neg)
    b = np.clip((b / base[0]) * 255, 0, 255)
    g = np.clip((g / base[1]) * 255, 0, 255)
    r = np.clip((r / base[2]) * 255, 0, 255)
    res = cv2.merge((b.astype(np.uint8), g.astype(np.uint8), r.astype(np.uint8)))
    return 255 - res

# Function to apply gamma correction
def adjust_gamma(image, gamma):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

# Function to apply white balance using Gray World Assumption
def apply_white_balance(image):
    avg_b = np.mean(image[:, :, 0])
    avg_g = np.mean(image[:, :, 1])
    avg_r = np.mean(image[:, :, 2])
    avg_gray = (avg_b + avg_g + avg_r) / 3

    scale_b = avg_gray / avg_b
    scale_g = avg_gray / avg_g
    scale_r = avg_gray / avg_r

    balanced_img = cv2.merge([
        np.clip(image[:, :, 0] * scale_b, 0, 255).astype(np.uint8),
        np.clip(image[:, :, 1] * scale_g, 0, 255).astype(np.uint8),
        np.clip(image[:, :, 2] * scale_r, 0, 255).astype(np.uint8)
    ])
    return balanced_img

# Function to adjust RGB channels
def adjust_rgb(image, r_factor, g_factor, b_factor):
    b, g, r = cv2.split(image)
    b = np.clip(b * b_factor, 0, 255).astype(np.uint8)
    g = np.clip(g * g_factor, 0, 255).astype(np.uint8)
    r = np.clip(r * r_factor, 0, 255).astype(np.uint8)
    return cv2.merge((b, g, r))

# Initialize session state variables
if 'manual_mode' not in st.session_state:
    st.session_state.manual_mode = False
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None

# UI
st.title("🎞️ Rollshift AI - Film Negative Processor")
uploaded_file = st.file_uploader("Upload a film scan", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image = np.array(image)
    rawscan = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # Automatic Processing Pipeline (Using the original defaults)
    base_color = find_base(rawscan)
    inverted_image = invert(rawscan, base_color)
    white_balanced_image = apply_white_balance(inverted_image)
    gamma_corrected_image = adjust_gamma(white_balanced_image, gamma=0.5)

    st.session_state.processed_image = gamma_corrected_image  # Save the processed image in session state
    
    # Display auto-adjusted image only if manual mode is off
    if not st.session_state.manual_mode:
        # Before-After Image Comparison (Raw Scan vs. Auto-Processed)
        image_comparison(
            img1=cv2.cvtColor(rawscan, cv2.COLOR_BGR2RGB), 
            img2=cv2.cvtColor(st.session_state.processed_image, cv2.COLOR_BGR2RGB), 
            label1="Raw Scan", 
            label2="Auto-Processed"
        )


        # Button to enter Manual Mode
        if st.button("Manual Mode"):
            st.session_state.manual_mode = True  # Enable manual mode

    # Show manual adjustments only in manual mode
    if st.session_state.manual_mode:
        st.subheader("Manual Adjustments")
        
        # Layout sliders side by side for better control
        col1, col2, col3 = st.columns(3)
        with col1:
            gamma_value = st.slider("Gamma", 0.5, 2.5, 0.5, 0.05)
        with col2:
            r_factor = st.slider("Red", 0.5, 2.0, 1.0, 0.05)
        with col3:
            g_factor = st.slider("Green", 0.5, 2.0, 1.0, 0.05)
        
        # Blue slider takes the full width for precision
        b_factor = st.slider("Blue", 0.5, 2.0, 1.0, 0.05)

        # Apply manual adjustments
        gamma_corrected_image = adjust_gamma(white_balanced_image, gamma_value)
        rgb_adjusted_image = adjust_rgb(gamma_corrected_image, r_factor, g_factor, b_factor)
        processed_image_manual = cv2.cvtColor(rgb_adjusted_image, cv2.COLOR_BGR2RGB)

        # Display manually adjusted image
        st.image(processed_image_manual, caption="Manually Adjusted Image", use_container_width=True)
