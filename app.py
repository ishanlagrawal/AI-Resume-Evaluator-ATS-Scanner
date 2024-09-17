
## pip install pymupdf

'''
1. Field to put JD
2. Upload PDF
3. PDF to image -->processing--> Google Gemini Pro
4. Prompt Template [Multiple Prompts]
'''
import os
import io
import base64
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import fitz  # PyMuPDF for PDF to image conversion
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get Google Gemini Pro response
def get_gemini_response(prompt, pdf_content, job_description):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content([job_description, pdf_content[0], prompt])
        return response.text
    except Exception as e:
        return f"Error in generating response: {e}"

# Function to convert the first page of a PDF to an image
def convert_pdf_to_image(uploaded_file):
    try:
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        first_page = pdf_document.load_page(0)
        pix = first_page.get_pixmap()
        
        # Save image as PNG in memory
        img_byte_arr = io.BytesIO(pix.tobytes(output="png"))
        img_byte_arr.seek(0)

        # Encode image to base64 format
        return [
            {
                "mime_type": "image/png",
                "data": base64.b64encode(img_byte_arr.read()).decode()  # base64 encoding
            }
        ]
    except Exception as e:
        st.error(f"Error in processing PDF: {e}")
        return None

# Streamlit App UI
st.set_page_config(page_title="AI-Powered Resume Evaluator")
st.header("AI Resume Evaluator & ATS Scanner")

# Input fields
job_description = st.text_area("Enter Job Description:", key="job_description")
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

# Button triggers
submit1 = st.button("Evaluate Resume")
submit3 = st.button("Calculate Match Percentage")

# Common prompts for evaluation and percentage matching
evaluation_prompt = """
You are an experienced HR with tech knowledge in Data Science, Full Stack Web Development, 
Big Data Engineering, DEVOPS, or Data Analysis. Your task is to review the resume against the job description.
Provide a professional evaluation on whether the profile aligns with the job requirements. 
Highlight strengths and weaknesses of the candidate.
"""

percentage_match_prompt = """
You are a skilled ATS (Applicant Tracking System) with deep understanding of Data Science, 
Full Stack Web Development, Big Data Engineering, DEVOPS, or Data Analysis. 
Evaluate the resume against the job description. First, give the match percentage, 
then list missing keywords, and finally provide your overall thoughts.
"""

# Process the uploaded PDF and generate results
def process_request(prompt):
    if uploaded_file is None:
        st.error("Please upload a PDF file of your resume.")
        return

    pdf_content = convert_pdf_to_image(uploaded_file)
    if pdf_content is None:
        return
    
    response = get_gemini_response(prompt, pdf_content, job_description)
    st.subheader("Response")
    st.write(response)

# Evaluate resume (professional assessment)
if submit1:
    process_request(evaluation_prompt)

# Calculate ATS match percentage
elif submit3:
    process_request(percentage_match_prompt)
