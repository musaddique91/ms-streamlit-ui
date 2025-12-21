import streamlit as st
from ascii_magic import AsciiArt
from PIL import Image
import io
import tempfile
import os
import numpy as np


def face_to_ascii():
    st.title("🎨 Image to ASCII Art Converter")
    st.write("Upload an image to convert it to beautiful ASCII art!")

    # Image upload section
    uploaded_image = st.file_uploader(
        "Choose an image...",
        type=["jpg", "png", "jpeg", "bmp"]
    )
    if uploaded_image:
        img = Image.open(uploaded_image)
        img_prev_col, img_ascii_prev_col = st.columns(2)
        with img_prev_col:
            st.image(img, caption="Original Image")
        with img_ascii_prev_col:
            charset = st.selectbox("Character Set", [
                "@%#*+=-:. ",
                " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
                " . ░▒▓█",
                " .:-=+*#%@"
            ])
            width = 50
            gray_img = img.convert("L").resize((width, int(width * img.height / img.width * 0.5)))
            pixels = np.array(gray_img)
            ascii_art = "\n".join(
                "".join(charset[min(int(p / 255 * (len(charset) - 1)), len(charset) - 1)] for p in row) for row in
                pixels)

            st.subheader("ASCII Art")
            st.code(ascii_art)

            st.download_button(
                label="Download ASCII Art",
                data=ascii_art,
                file_name="ascii_art.txt",
                mime="text/plain"
            )
