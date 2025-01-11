import pandas as pd
import streamlit as st
from pytesseract import pytesseract
from pdf2image import convert_from_path
import os
import csv
from PIL import Image
from datetime import datetime
import requests

# Path to Tesseract executable
pytesseract.tesseract_cmd = r"C:\\Users\\Pc\\tesseract.exe"  # Update this path if necessary
poppler_path = r"C:\\poppler-24.07.0\\Library\\bin"
API_BASE_URL = "http://localhost:8000/api"
def save_to_csv(file_name, data):
    csv_file_path = os.path.join("output", file_name)
    os.makedirs("output", exist_ok=True)  # Ensure output directory exists
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["Parameter", "Value"])
        # Write data
        for key, value in data.items():
            writer.writerow([key, value])
    return csv_file_path
def calculate_age(dob_input):
    try:
        dob = datetime.strptime(dob_input, "%d/%m/%Y")  # Ensure format is DD/MM/YYYY
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except ValueError:
        return "Invalid DOB Format"

# Calculate Age

# Streamlit app
def main():
    st.title("PDF OCR Application with Authentication")

    # User authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        auth_mode = st.radio("Choose Authentication Mode", ["Login", "Sign Up"])

        if auth_mode == "Login":
            st.subheader("User Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                response = requests.post(f"{API_BASE_URL}/login/", data={"username": username, "password": password})
                if response.status_code == 200:
                    st.session_state["authenticated"] = True
                    st.success("Login successful!")
                else:
                    st.error("Invalid credentials. Please try again.")

        elif auth_mode == "Sign Up":
            st.subheader("User Sign Up")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Sign Up"):
                response = requests.post(f"{API_BASE_URL}/signup/", data={"username": username, "email": email, "password": password})
                if response.status_code == 201:
                    st.success("Account created successfully! Please log in.")
                else:
                    st.error(response.json().get("error", "An error occurred during sign-up."))

        return

    st.write("Upload a PDF file to extract text using OCR and check for specific parameters.")

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    # User input for parameters
    st.sidebar.header("Input Parameters")
    dob_input = st.sidebar.text_input("Date of Birth (DD/MM/YYYY)")
    sex_input = st.sidebar.text_input("Sex")
    occupation_input = st.sidebar.text_input("Occupation")
    education_input = st.sidebar.text_input("Educational Qualification")
    income_input = st.sidebar.text_input("Annual Income")
    place_of_birth_input = st.sidebar.text_input("Place of Birth")

    if uploaded_file is not None:
        with st.spinner("Processing your file..."):
            # Save uploaded file temporarily
            temp_pdf_path = os.path.join("temp_upload.pdf")
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Convert PDF to images
            images = convert_from_path(temp_pdf_path, poppler_path=poppler_path)

            extracted_text = ""

            for i, page in enumerate(images):
                st.image(page, caption=f"Page {i + 1}", use_column_width=True)

                # Perform OCR on each page
                text = pytesseract.image_to_string(page, lang='eng')
                extracted_text += f"\n--- Page {i + 1} ---\n{text}"
                age = calculate_age(dob_input)
                structured_data = {
                "Date of Birth": dob_input,
                "Age": str(age) if isinstance(age, int) else "Invalid DOB" ,
                "Sex": sex_input,
                "Occupation": occupation_input,
                "Education Level": education_input,
                "Annual Income": income_input,
                "Place of Birth": place_of_birth_input,
} 

# Save to CSV
                csv_file_path = save_to_csv("extracted_user_profile.csv", structured_data)
                st.write(f"Structured data saved to CSV: {csv_file_path}")

            # Display extracted text
            st.subheader("Extracted Text")
            st.text_area("", extracted_text, height=300)
            
            # Check for parameters in extracted text
            st.subheader("Parameter Check")
            def check_presence(param_name, param_value):
                if param_value and param_value in extracted_text:
                    st.write(f"{param_name}: Found")
                else:
                    st.write(f"{param_name}: Not Found")

            # Calculate Age from DOB if provided
            age = None
            if dob_input:
                try:
                    dob = datetime.strptime(dob_input, "%d/%m/%Y")
                    today = datetime.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    st.sidebar.write(f"Calculated Age: {age}")
                except ValueError:
                    st.sidebar.write("Invalid Date of Birth format. Please use DD/MM/YYYY.")

            check_presence("Date of Birth", dob_input)
            check_presence("Age", str(age) if age else None)
            check_presence("Sex", sex_input)
            check_presence("Occupation", occupation_input)
            check_presence("Educational Qualification", education_input)
            check_presence("Annual Income", income_input)
            check_presence("Place of Birth", place_of_birth_input)

            # Provide a download link for the text
            st.download_button(
                label="Download Extracted Text",
                data=extracted_text,
                file_name="extracted_text.txt",
                mime="text/plain",
            )

            # Clean up temporary files
            os.remove(temp_pdf_path)

if __name__ == "__main__":
    main()
