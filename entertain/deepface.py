import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image
import os
print("deepface")
def show_deepface_page():
    print("show_deepface_page")
    st.title("Welcome to Deep Face Dashboard")
    
    tab1, tab2 = st.tabs(["Match Face", "Face Details"])
    with tab1:
        st.header("Upload Two Images to Verify Match")
        col1, col2 = st.columns(2)
        image1, image2 = None, None  # Initialize variables
        with col1:
            uploaded_file1 = st.file_uploader("Upload Image 1", type=["jpg", "png", "jpeg"])
            if uploaded_file1:
                image1 = Image.open(uploaded_file1)
                st.image(image1, caption="First Image", use_column_width=True)
        with col2:
            uploaded_file2 = st.file_uploader("Upload Image 2", type=["jpg", "png", "jpeg"])
            if uploaded_file2:
                image2 = Image.open(uploaded_file2)
                st.image(image2, caption="Second Image", use_column_width=True)

        if uploaded_file1 and uploaded_file2:
            if st.button("Verify Faces 🔍"):
                # Save images temporarily
                img1_path = "temp1.jpg"
                img2_path = "temp2.jpg"
                image1.save(img1_path)
                image2.save(img2_path)

                # Perform Face Verification
                with st.spinner("Analyzing... 🔄"):
                    result = DeepFace.verify(img1_path, img2_path)

                # Display Result
                if result["verified"]:
                    st.success("✅ Faces Match!")
                else:
                    st.error("❌ Faces Do Not Match!")
                st.title("Match Face Details")
                st.write(result)

                # Remove Temporary Files
                os.remove(img1_path)
                os.remove(img2_path)
    with tab2:
        st.header("Upload Image to see details")
        uploaded_file3 = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
        if uploaded_file3:
            image1 = Image.open(uploaded_file3)
            st.image(image1, caption="First Image", use_container_width=True)
            img1_array = np.array(image1)
            with st.spinner("Analysing image..."):
                analysis = DeepFace.analyze(img1_array,
                                        actions=["age", "gender", "emotion", "race"],
                                        detector_backend="mtcnn",
                                        enforce_detection=True
                                        )
            st.write(analysis)
            for face in analysis:
                age = face['age']
                dominant_gender = face['dominant_gender']
                dominant_emotion = face['dominant_emotion']
                st.write(f"Age: {age}, Gender: {dominant_gender}, Dominant Emotion: {dominant_emotion}")