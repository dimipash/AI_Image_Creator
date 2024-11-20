from openai import OpenAI
from PIL import Image
import streamlit as st
import os
from dotenv import load_dotenv
from streamlit_carousel import carousel

# Constants
PAGE_TITLE = "AI Image Creator"
PAGE_ICON = "🎨"
LAYOUT = "wide"
SIDEBAR_STATE = "expanded"
SINGLE_IMAGE_TEMPLATE = {"title": "", "text": "", "interval": 0, "img": ""}
CSS_FILE_PATH = "static/style.css"
TIPS_HTML = """
<div class="tips-container">
<h3>💡 Tips for better results:</h3>
1. Be specific and detailed<br>
2. Include art style preferences<br>
3. Mention colors and lighting<br>
4. Describe composition<br>
5. Add contextual elements
</div>
"""
FOOTER_HTML = """<div class="footer">
Made with 💜 using DALL-E 3 | © 2024
</div>"""

# Configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE,
)
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Load custom CSS
def load_custom_css(css_path):
    with open(css_path) as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


load_custom_css(CSS_FILE_PATH)


# Generate images
def generate_images(prompt, count):
    with st.spinner("🎨 Creating your masterpiece..."):
        gallery = []
        for i in range(count):
            try:
                response = openai_client.images.generate(
                    model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1
                )
                image_info = create_image_info(response, prompt, i)
                gallery.append(image_info)
            except Exception as error:
                st.error(f"An error occurred: {str(error)}")
                return None
        return gallery


def create_image_info(response, prompt, index):
    image_url = response.data[0].url
    new_image = dict(SINGLE_IMAGE_TEMPLATE)
    new_image["title"] = f"Creation {index + 1}"
    new_image["text"] = (prompt[:50] + "...") if len(prompt) > 50 else prompt
    new_image["interval"] = 2000
    new_image["img"] = image_url
    return new_image


def display_main_content():
    st.markdown('<p class="title-text">AI Image Creator</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle-text">Transform your ideas into stunning visuals using DALL-E 3</p>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([2, 1])
    with col1:
        img_description = st.text_area(
            "🎯 Describe your image",
            placeholder="Be as detailed as possible. For example: A cyberpunk cityscape at night with neon lights, hovering vehicles, and holographic advertisements reflecting in rain puddles",
            height=100
        )
        col3, col4 = st.columns([3, 1])
        with col3:
            num_of_images = st.slider(
                "🖼️ Number of images",
                min_value=1,
                max_value=4,
                value=1,
                help="Generate multiple variations of your description"
            )
        with col4:
            generate_button = st.button("✨ Generate", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.markdown(TIPS_HTML, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    return img_description, num_of_images, generate_button


def handle_image_generation(img_description, num_of_images):
    if img_description:
        generated_images = generate_images(img_description, num_of_images)
        if generated_images:
            st.markdown("### 🎨 Your Generated Images")
            carousel(items=generated_images, width=1000)
            st.markdown("### ⬇️ Download Images")
            for idx, img in enumerate(generated_images):
                st.markdown(
                    f'<a href="{img["img"]}" class="download-button" target="_blank">Download Image {idx + 1}</a>',
                    unsafe_allow_html=True
                )
                # Link to view full-sized image
                st.markdown(
                    f'<a href="{img["img"]}" target="_blank">View Full-Sized Image {idx + 1}</a>',
                    unsafe_allow_html=True
                )
    else:
        st.warning("Please enter a description for your image!")



def main():
    """
    Main function that manages the display and handling of image generation
    functionality.

    :return: None
    :rtype: None
    """
    img_description, num_of_images, generate_button = display_main_content()
    if generate_button:
        handle_image_generation(img_description, num_of_images)
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)


main()
