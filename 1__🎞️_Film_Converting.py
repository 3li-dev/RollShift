import streamlit as st
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import time
import base64

from streamlit_image_comparison import image_comparison
st.set_page_config(
        page_title="RollShift AI",
        page_icon="media/brand/RS_Fav.png",
        layout="centered",
 
)
# Function to encode font file
def get_base64_font(font_path):
    with open(font_path, "rb") as font_file:
        return base64.b64encode(font_file.read()).decode("utf-8")

# Convert OTF file to Base64
font_base64 = get_base64_font("media/fonts/Bristol.otf")  # Adjust the path


# Display the logo in the sidebar with a small size
st.logo("media/brand/RS_logo.png", size="large")  # Replace 'logo.png' with your image path or URL


st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 200px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

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

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bristol&display=swap');
        section[data-testid="stSidebar"] {
            width: 200px !important;
        }
        .stDownloadButton>button, .stButton>button {
            width: 100% !important;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        }
        h1 {
            font-family: 'Bristol', sans-serif;
        }
    </style>
    <h1 style="text-align: center;">RollShift AI</h1>
    """,
    unsafe_allow_html=True,
    
)
# Function to find base color using the 99th percentile of brightness
def find_base(neg):
    flat_img = neg.reshape(-1, 3)  # Flatten image into (N, 3) array
    brightness = np.sum(flat_img, axis=1)  # Compute brightness for each pixel
    idx = np.argsort(brightness)[-int(0.01 * len(brightness)):]  # Get top 1% brightest pixels
    white_sample = np.mean(flat_img[idx], axis=0)  # Compute mean base color for BGR
    return white_sample  # Returns (B, G, R) as a NumPy array



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

#auto gamma correction
def auto_gamma_correction(image):
    mean_intensity = np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    gamma = np.clip(1.5 - (mean_intensity / 128), 0.4, 2.5)  # Adjust dynamically
    return adjust_gamma(image, gamma)


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

def white_patch_retinex(image):
    max_b = np.max(image[:, :, 0])
    max_g = np.max(image[:, :, 1])
    max_r = np.max(image[:, :, 2])

    scale_b = 255 / max_b
    scale_g = 255 / max_g
    scale_r = 255 / max_r

    balanced_img = cv2.merge([
        np.clip(image[:, :, 0] * scale_b, 0, 255).astype(np.uint8),
        np.clip(image[:, :, 1] * scale_g, 0, 255).astype(np.uint8),
        np.clip(image[:, :, 2] * scale_r, 0, 255).astype(np.uint8)
    ])
    
    return balanced_img

def apply_clahe(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)

    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

def auto_color_balance(image):
    white_balanced = apply_white_balance(image)
    retinex_balanced = white_patch_retinex(white_balanced)
    final_image = apply_clahe(retinex_balanced)
    
    return final_image


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


def apply_lab_white_balance(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Auto-correct color channels
    a_mean = np.mean(a)
    b_mean = np.mean(b)

    a = np.clip(a - (a_mean - 128), 0, 255)  # Adjust red-green balance
    b = np.clip(b - (b_mean - 128), 0, 255)  # Adjust blue-yellow balance

    corrected = cv2.merge([l, a.astype(np.uint8), b.astype(np.uint8)])
    return cv2.cvtColor(corrected, cv2.COLOR_LAB2BGR)


def dynamic_red_reduction(image):
    b, g, r = cv2.split(image)

    avg_b = np.mean(b)
    avg_g = np.mean(g)
    avg_r = np.mean(r)

    # Calculate how much red is over-dominating
    red_balance = np.clip(1.0 - ((avg_r - ((avg_b + avg_g) / 2)) / 255), 0.7, 1.0)

    # Apply correction only if red is dominant
    if avg_r > (avg_b + avg_g) / 2:
        r = np.clip(r * red_balance, 0, 255)

    return cv2.merge((b.astype(np.uint8), g.astype(np.uint8), r.astype(np.uint8)))


def auto_color_balance(image):
    lab_balanced = apply_lab_white_balance(image)  # Step 1: LAB-based balance
    red_fixed = dynamic_red_reduction(lab_balanced)  # Step 2: Adjust red dynamically
    final_image = apply_clahe(red_fixed)  # Step 3: CLAHE for better contrast
    return final_image


st.markdown(
    """
   <p style="text-align: center; font-size: 16px;">Where Innovation Meets Tradition! ✨</p>
    """,
    unsafe_allow_html=True
)
st.markdown(f"""
    <style>
        @font-face {{
            font-family: 'Bristol';
            src: url(data:font/otf;base64,{font_base64}) format('opentype');
        }}
        h1 {{
            font-family: 'Bristol', sans-serif !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Display title using the Bristol font


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
        ("Color Balanced Image", auto_color_balance(invert(rawscan, find_base(rawscan)))),
        ("Gamma Corrected Image", auto_gamma_correction(apply_white_balance(invert(rawscan, find_base(rawscan))))),
        ("Sharpened Image", sharp(adjust_gamma(apply_white_balance(invert(rawscan, find_base(rawscan))), gamma=0.5)))
    ]
    
    with st.spinner("📸 Processing your film... Hang tight!"):
        placeholder = st.empty()
        for label, img in processing_steps:
            placeholder.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption=label, use_container_width=True)
            time.sleep(1)  # Smooth transition effect
        placeholder.empty()
    
    final_image = processing_steps[-1][1]
    
    # Image Comparison at the End
    image_comparison(
        img1=cv2.cvtColor(rawscan, cv2.COLOR_BGR2RGB), 
        img2=cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB), 
        label1="Raw Scan", 
        label2="RollShift Processed"
    )
    
    processed_pil = Image.fromarray(cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB))
    buf = BytesIO()
    processed_pil.save(buf, format="JPEG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download Your Positive 📥",
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
