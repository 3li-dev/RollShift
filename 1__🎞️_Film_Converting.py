import streamlit as st
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import time
from streamlit_image_comparison import image_comparison

st.markdown("""
    <style>
        .stDownloadButton>button, .stButton>button {
            width: 100% !important;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Function to find base color using the 99th percentile of brightness
def find_base(neg):
    flat_img = neg.reshape(-1, 3)
    brightness = np.sum(flat_img, axis=1)
    idx = np.argsort(brightness)[-int(0.01 * len(brightness)):]  
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

# Function to sharpen image
def sharp(image):
    kernel = np.array([[0, -0.25, 0], 
                    [-0.25, 2, -0.25], 
                    [0, -0.25, 0]])    
    sharp_img = cv2.filter2D(image, -1, kernel)
    return sharp_img

st.title("RollShift AI - Film Negative Processor 🎞️")
st.write("Where Innovation Meets Tradition! ✨")

if 'manual_mode' not in st.session_state:
    st.session_state.manual_mode = False

uploaded_file = st.file_uploader("Upload a film scan", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image = np.array(image)
    rawscan = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # Animated step-by-step processing
    processing_steps = [
        ("Raw Scan", rawscan),
        ("Inverted Image", invert(rawscan, find_base(rawscan))),
        ("White Balanced Image", apply_white_balance(invert(rawscan, find_base(rawscan)))),
        ("Gamma Corrected Image", adjust_gamma(apply_white_balance(invert(rawscan, find_base(rawscan))), gamma=0.5)),
        ("Sharpened Image", sharp(adjust_gamma(apply_white_balance(invert(rawscan, find_base(rawscan))), gamma=0.5)))
    ]
    
    placeholder = st.empty()
    for label, img in processing_steps:
        placeholder.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption=label, use_container_width=True)
        time.sleep(1)  # Smooth transition effect
    
    # Clear placeholder after showing steps
    placeholder.empty()
    
    final_image = processing_steps[-1][1]
    
    # Image Comparison at the End
    image_comparison(
        img1=cv2.cvtColor(rawscan, cv2.COLOR_BGR2RGB), 
        img2=cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB), 
        label1="Raw Scan", 
        label2="Final Processed Image"
    )
    
    processed_pil = Image.fromarray(cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB))
    buf = BytesIO()
    processed_pil.save(buf, format="JPEG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download Processed Image 📥",
        data=byte_im,
        file_name="processed_image.jpg",
        mime="image/jpeg"
    )
    
    if st.button("Switch to Manual Mode 🛠️"):
        st.session_state.manual_mode = True
    
    if st.session_state.manual_mode:
        st.subheader("🎨 Manual Adjustments")
        gamma_value = st.slider("Gamma", 0.5, 2.5, 1.0, 0.05)
        r_factor = st.slider("Red", 0.5, 2.0, 1.0, 0.05)
        g_factor = st.slider("Green", 0.5, 2.0, 1.0, 0.05)
        b_factor = st.slider("Blue", 0.5, 2.0, 1.0, 0.05)
        
        adjusted_image = adjust_gamma(final_image, gamma_value)
        adjusted_image = adjust_rgb(adjusted_image, r_factor, g_factor, b_factor)
        
        st.image(cv2.cvtColor(adjusted_image, cv2.COLOR_BGR2RGB), caption="Manually Adjusted Image", use_container_width=True)
