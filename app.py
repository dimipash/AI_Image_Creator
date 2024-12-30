from typing import List, Dict, Optional
from openai import OpenAI, OpenAIError
import streamlit as st
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Configuration
PAGE_TITLE = "AI Image Creator"
PAGE_ICON = "🎨"
LAYOUT = "wide"
MAX_PROMPT_LENGTH = 1000
MAX_IMAGES = 4
CSS_FILE_PATH = "static/style.css"

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=MAX_PROMPT_LENGTH)
    count: int = Field(1, ge=1, le=MAX_IMAGES)
    style: Optional[str] = None
    quality: str = "standard"
    size: str = "1024x1024"

    @validator('prompt')
    def validate_prompt(cls, value):
        if len(value.strip()) < 10:
            raise ValueError('Prompt must be at least 10 characters')
        return value.strip()

def init_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)

def load_custom_css():
    with open(CSS_FILE_PATH) as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

def generate_images(request: ImageGenerationRequest) -> Optional[List[Dict]]:
    with st.spinner("🎨 Creating your masterpiece..."):
        gallery = []
        for _ in range(request.count):
            try:
                response = openai_client.images.generate(
                    model="dall-e-3",
                    prompt=request.prompt,
                    size=request.size,
                    quality=request.quality,
                    n=1,
                    style=request.style
                )
                image_info = {
                    "title": f"Creation {len(gallery) + 1}",
                    "text": (request.prompt[:50] + "...") if len(request.prompt) > 50 else request.prompt,
                    "interval": 2000,
                    "img": response.data[0].url
                }
                gallery.append(image_info)
            except OpenAIError as error:
                st.error(f"API Error: {str(error)}")
                return None
            except Exception as error:
                st.error(f"An unexpected error occurred: {str(error)}")
                return None
        return gallery

def display_ui():
    st.markdown('<p class="title-text">AI Image Creator</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Transform your ideas into stunning visuals using DALL-E 3</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        img_description = st.text_area(
            "🎯 Describe your image",
            placeholder="Be as detailed as possible...",
            height=100
        )
        
        with st.expander("⚙️ Advanced Settings"):
            col3, col4 = st.columns(2)
            with col3:
                style = st.selectbox(
                    "🎨 Art Style",
                    options=["vivid", "natural"],
                    help="Choose between vivid (more dramatic) or natural (more realistic) styles"
                )
                quality = st.radio("✨ Quality", options=["Standard", "HD"], index=0, horizontal=True)
                
            with col4:
                num_of_images = st.slider("🖼️ Number of images", 1, 4, 1)
                size = st.radio("📐 Size", options=["1024x1024", "1024x1792", "1792x1024"], index=0, horizontal=True)
        
        generate_button = st.button("✨ Generate", use_container_width=True)

    with col2:
        if 'generated_images' in st.session_state and st.session_state.generated_images:
            latest_image = st.session_state.generated_images[-1]
            st.markdown("### 🎨 Latest Creation")
            st.image(latest_image["img"], use_column_width=True)
            st.markdown(f'<a href="{latest_image["img"]}" class="download-button" target="_blank">Download Image</a>', unsafe_allow_html=True)

    return img_description, num_of_images, generate_button, style, quality, size

def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
    load_dotenv()
    
    global openai_client
    try:
        openai_client = init_openai_client()
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {str(e)}")
        st.stop()
    
    load_custom_css()
    
    img_description, num_of_images, generate_button, style, quality, size = display_ui()
    
    if generate_button and img_description:
        try:
            request = ImageGenerationRequest(
                prompt=img_description,
                count=num_of_images,
                style=style,
                quality=quality.lower(),
                size=size
            )
            
            generated_images = generate_images(request)
            if generated_images:
                if 'generated_images' not in st.session_state:
                    st.session_state.generated_images = []
                st.session_state.generated_images.extend(generated_images)
                
                if len(st.session_state.generated_images) > 1:
                    st.markdown("### 📚 Generation History")
                    history_cols = st.columns(min(4, len(st.session_state.generated_images)))
                    for idx, img in enumerate(reversed(st.session_state.generated_images[:-1])):
                        with history_cols[idx % len(history_cols)]:
                            st.image(img["img"], use_column_width=True)
                            st.markdown(f'<a href="{img["img"]}" class="download-button" target="_blank">Download</a>', unsafe_allow_html=True)
        except ValueError as e:
            st.error(str(e))
    elif generate_button:
        st.warning("Please enter a description for your image!")
    
    st.markdown('<div class="footer">Made with 💜 using DALL-E 3 | © 2024</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
