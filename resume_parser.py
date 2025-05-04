import PyPDF2
import json
from typing import Dict
from google import genai

class ResumeParser:
    def __init__(self, api_key: str):
        # Initialize the Google GenAI client with the API key
        self.client = genai.Client(api_key=api_key)
        # Use the model that's compatible with the current API version
        self.model = self.client.models
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def parse_resume(self, pdf_path: str) -> Dict:
        pdf_text = self.extract_text_from_pdf(pdf_path)
        
        prompt = f"""
        Extract the following information from this resume:
        1. Full Name
        2. Email
        3. Phone Number
        4. Location
        5. Summary/Objective
        6. Skills (list)
        7. Work Experience (list of jobs with title, company, dates, responsibilities)
        8. Education (list of degrees with institution, dates)
        9. Certifications (if any)
        10. Projects (if any)
        
        Resume text:
        {pdf_text}
        
        Return the information in JSON format.
        """
        
        response = self.model.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt
        )
        return json.loads(response.text)