import PyPDF2
import pandas as pd
import re
import json
from typing import Dict, List, Any

class ResumePDFToCSV:
    def __init__(self):
        self.resume_data = {
            'name': '',
            'email': '',
            'phone': '',
            'address': '',
            'summary': '',
            'education': '',
            'skills': '',
            'experience': '',
            'certifications': '',
            'projects': '',
            'languages': '',
            'achievements': ''
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
    
    def extract_email(self, text: str) -> str:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""
    
    def extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        phone_patterns = [
            r'\+?1?[-.\s]?$$?([0-9]{3})$$?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\+?([0-9]{1,3})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})',
            r'(\d{10})',
            r'\+\d{1,3}\s?\d{3,4}\s?\d{3,4}\s?\d{3,4}'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    return ''.join(matches[0])
                return matches[0]
        return ""
    
    def extract_name(self, text: str) -> str:
        """Extract name from the beginning of the resume"""
        lines = text.split('\n')
        # Usually name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
                # Check if it's not an email or common resume words
                if '@' not in line and not any(word.lower() in line.lower() 
                    for word in ['resume', 'cv', 'curriculum', 'vitae', 'profile']):
                    return line
        return ""
    
    def extract_section_content(self, text: str, section_keywords: List[str], 
                              next_section_keywords: List[str] = None) -> str:
        """Extract content of a specific section"""
        text_lower = text.lower()
        
        # Find section start
        section_start = -1
        for keyword in section_keywords:
            pattern = rf'\b{re.escape(keyword.lower())}\b'
            match = re.search(pattern, text_lower)
            if match:
                section_start = match.start()
                break
        
        if section_start == -1:
            return ""
        
        # Find section end
        section_end = len(text)
        if next_section_keywords:
            for keyword in next_section_keywords:
                pattern = rf'\b{re.escape(keyword.lower())}\b'
                match = re.search(pattern, text_lower[section_start + 50:])
                if match:
                    section_end = section_start + 50 + match.start()
                    break
        
        section_content = text[section_start:section_end].strip()
        # Clean up the content
        lines = section_content.split('\n')
        cleaned_lines = [line.strip() for line in lines[1:] if line.strip()]
        return ' | '.join(cleaned_lines)
    
    def parse_resume(self, pdf_path: str) -> Dict[str, Any]:
        """Main function to parse resume and extract all information"""
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            print("Could not extract text from PDF")
            return self.resume_data
        
        # Extract basic information
        self.resume_data['name'] = self.extract_name(text)
        self.resume_data['email'] = self.extract_email(text)
        self.resume_data['phone'] = self.extract_phone(text)
        
        # Extract sections
        sections_config = [
            {
                'key': 'summary',
                'keywords': ['summary', 'profile', 'objective', 'about'],
                'next_keywords': ['experience', 'education', 'skills', 'work']
            },
            {
                'key': 'experience',
                'keywords': ['experience', 'work experience', 'employment', 'work history'],
                'next_keywords': ['education', 'skills', 'projects', 'certifications']
            },
            {
                'key': 'education',
                'keywords': ['education', 'academic', 'qualification', 'degree'],
                'next_keywords': ['skills', 'experience', 'projects', 'certifications']
            },
            {
                'key': 'skills',
                'keywords': ['skills', 'technical skills', 'competencies', 'technologies'],
                'next_keywords': ['experience', 'education', 'projects', 'certifications']
            },
            {
                'key': 'projects',
                'keywords': ['projects', 'project experience', 'key projects'],
                'next_keywords': ['skills', 'education', 'certifications', 'achievements']
            },
            {
                'key': 'certifications',
                'keywords': ['certifications', 'certificates', 'licenses'],
                'next_keywords': ['skills', 'projects', 'achievements', 'languages']
            },
            {
                'key': 'achievements',
                'keywords': ['achievements', 'awards', 'honors', 'accomplishments'],
                'next_keywords': ['languages', 'references', 'interests']
            },
            {
                'key': 'languages',
                'keywords': ['languages', 'language skills'],
                'next_keywords': ['references', 'interests', 'hobbies']
            }
        ]
        
        for section in sections_config:
            content = self.extract_section_content(
                text, 
                section['keywords'], 
                section['next_keywords']
            )
            self.resume_data[section['key']] = content
        
        return self.resume_data
    
    def save_to_csv(self, data: Dict[str, Any], output_path: str):
        """Save extracted data to CSV file"""
        df = pd.DataFrame([data])
        df.to_csv(output_path, index=False)
        print(f"Resume data saved to {output_path}")
        
        # Display the extracted data
        print("\nExtracted Resume Data:")
        print("-" * 50)
        for key, value in data.items():
            print(f"{key.upper()}: {value[:100]}{'...' if len(str(value)) > 100 else ''}")
    
    def process_resume(self, pdf_path: str, csv_output_path: str = "resume_data.csv"):
        """Complete process: PDF to CSV conversion"""
        print(f"Processing resume: {pdf_path}")
        
        # Parse the resume
        extracted_data = self.parse_resume(pdf_path)
        
        # Save to CSV
        self.save_to_csv(extracted_data, csv_output_path)
        
        return extracted_data

# Example usage
if __name__ == "__main__":
    # Initialize the converter
    converter = ResumePDFToCSV()
    
    # Example: Process a resume PDF file
    # Replace 'sample_resume.pdf' with your actual PDF file path
    pdf_file_path = "sample_resume.pdf"  # Change this to your PDF file path
    csv_output_path = "extracted_resume_data.csv"
    
    try:
        # Process the resume
        result = converter.process_resume(pdf_file_path, csv_output_path)
        
        print(f"\n✅ Successfully converted {pdf_file_path} to {csv_output_path}")
        print(f"📊 Extracted {len([v for v in result.values() if v])} non-empty fields")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find the PDF file '{pdf_file_path}'")
        print("Please make sure the file exists and the path is correct.")
        
        # Create a sample CSV with empty data to show the structure
        sample_data = {
            'name': 'John Doe',
            'email': 'john.doe@email.com',
            'phone': '+1-555-123-4567',
            'address': '123 Main St, City, State',
            'summary': 'Experienced software developer with 5+ years...',
            'education': 'Bachelor of Science in Computer Science | XYZ University | 2018',
            'skills': 'Python | JavaScript | React | Node.js | SQL | Git',
            'experience': 'Software Developer | ABC Company | 2019-Present | Developed web applications...',
            'certifications': 'AWS Certified Developer | Google Cloud Professional',
            'projects': 'E-commerce Platform | Personal Portfolio Website',
            'languages': 'English (Native) | Spanish (Intermediate)',
            'achievements': 'Employee of the Month | Published research paper'
        }
        
        converter.save_to_csv(sample_data, "sample_resume_structure.csv")
        print(f"📝 Created sample CSV structure: sample_resume_structure.csv")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
