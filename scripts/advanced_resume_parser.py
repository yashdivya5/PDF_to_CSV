import PyPDF2
import pandas as pd
import re
from typing import Dict, List, Any
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class AdvancedResumePDFToCSV:
    def __init__(self):
        self.resume_data = {
            'name': '',
            'email': '',
            'phone': '',
            'address': '',
            'linkedin': '',
            'github': '',
            'website': '',
            'summary': '',
            'education': '',
            'skills': '',
            'experience': '',
            'certifications': '',
            'projects': '',
            'languages': '',
            'achievements': '',
            'interests': '',
            'references': ''
        }
        
        # Common section headers
        self.section_headers = {
            'summary': ['summary', 'profile', 'objective', 'about me', 'professional summary', 'career objective'],
            'experience': ['experience', 'work experience', 'employment history', 'professional experience', 'work history', 'career history'],
            'education': ['education', 'academic background', 'qualifications', 'academic qualifications', 'educational background'],
            'skills': ['skills', 'technical skills', 'core competencies', 'key skills', 'technologies', 'expertise'],
            'projects': ['projects', 'key projects', 'project experience', 'notable projects', 'personal projects'],
            'certifications': ['certifications', 'certificates', 'professional certifications', 'licenses', 'credentials'],
            'achievements': ['achievements', 'awards', 'honors', 'accomplishments', 'recognition'],
            'languages': ['languages', 'language skills', 'linguistic skills'],
            'interests': ['interests', 'hobbies', 'personal interests', 'activities'],
            'references': ['references', 'referees']
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file with better error handling"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {page_num + 1}: {e}")
                        continue
                return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract all contact information"""
        contact_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info['email'] = emails[0] if emails else ""
        
        # Phone extraction with multiple patterns
        phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\+?([0-9]{1,3})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})',
            r'(\d{10})',
            r'\+\d{1,3}\s?\d{3,4}\s?\d{3,4}\s?\d{3,4}'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    contact_info['phone'] = ''.join(matches[0])
                else:
                    contact_info['phone'] = matches[0]
                break
        else:
            contact_info['phone'] = ""
        
        # LinkedIn extraction
        linkedin_pattern = r'(?:linkedin\.com/in/|linkedin\.com/pub/)([A-Za-z0-9\-\.]+)'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        contact_info['linkedin'] = f"linkedin.com/in/{linkedin_matches[0]}" if linkedin_matches else ""
        
        # GitHub extraction
        github_pattern = r'(?:github\.com/)([A-Za-z0-9\-\.]+)'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        contact_info['github'] = f"github.com/{github_matches[0]}" if github_matches else ""
        
        # Website extraction
        website_pattern = r'(?:https?://)?(?:www\.)?([A-Za-z0-9\-\.]+\.[A-Za-z]{2,})'
        website_matches = re.findall(website_pattern, text)
        # Filter out email domains and common sites
        websites = [w for w in website_matches if not any(domain in w.lower() 
                   for domain in ['gmail', 'yahoo', 'outlook', 'linkedin', 'github'])]
        contact_info['website'] = websites[0] if websites else ""
        
        return contact_info
    
    def extract_name(self, text: str) -> str:
        """Enhanced name extraction"""
        lines = text.split('\n')
        
        # Look for name in first few lines
        for i, line in enumerate(lines[:7]):
            line = line.strip()
            if not line:
                continue
                
            # Skip lines with common resume words
            skip_words = ['resume', 'cv', 'curriculum', 'vitae', 'profile', 'contact', 'email', 'phone']
            if any(word in line.lower() for word in skip_words):
                continue
                
            # Skip lines with email or phone
            if '@' in line or re.search(r'\d{3,}', line):
                continue
                
            # Check if it looks like a name (2-4 words, mostly alphabetic)
            words = line.split()
            if 2 <= len(words) <= 4 and all(word.replace('-', '').replace("'", '').isalpha() for word in words):
                return line
                
        return ""
    
    def find_section_boundaries(self, text: str) -> Dict[str, tuple]:
        """Find start and end positions of each section"""
        text_lower = text.lower()
        section_positions = {}
        
        for section_key, keywords in self.section_headers.items():
            for keyword in keywords:
                # Look for keyword as section header (often followed by colon or newline)
                patterns = [
                    rf'\n\s*{re.escape(keyword)}\s*:',
                    rf'\n\s*{re.escape(keyword)}\s*\n',
                    rf'^{re.escape(keyword)}\s*:',
                    rf'^{re.escape(keyword)}\s*\n'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text_lower, re.MULTILINE)
                    if match:
                        section_positions[section_key] = match.start()
                        break
                
                if section_key in section_positions:
                    break
        
        return section_positions
    
    def extract_section_content(self, text: str, section_key: str, section_positions: Dict[str, tuple]) -> str:
        """Extract content between section boundaries"""
        if section_key not in section_positions:
            return ""
        
        start_pos = section_positions[section_key]
        
        # Find the next section to determine end position
        end_pos = len(text)
        for other_section, other_pos in section_positions.items():
            if other_section != section_key and other_pos > start_pos:
                end_pos = min(end_pos, other_pos)
        
        # Extract and clean the section content
        section_text = text[start_pos:end_pos]
        lines = section_text.split('\n')
        
        # Remove the section header line
        content_lines = []
        header_found = False
        
        for line in lines:
            line = line.strip()
            if not header_found:
                # Skip until we pass the header
                if any(keyword in line.lower() for keyword in self.section_headers[section_key]):
                    header_found = True
                continue
            
            if line:
                content_lines.append(line)
        
        return '\n'.join(content_lines)
    
    def parse_resume(self, pdf_path: str) -> Dict[str, Any]:
        """Parse resume and extract all information"""
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return self.resume_data
        
        # Extract basic information
        contact_info = self.extract_contact_info(text)
        name = self.extract_name(text)
        
        # Update resume data with basic info
        self.resume_data.update(contact_info)
        self.resume_data['name'] = name
        
        # Find section boundaries
        section_positions = self.find_section_boundaries(text)
        
        # Extract content for each section
        for section_key in self.section_headers.keys():
            content = self.extract_section_content(text, section_key, section_positions)
            self.resume_data[section_key] = content
        
        return self.resume_data
    
    def save_to_csv(self, data: Dict[str, Any], output_path: str):
        """Save extracted data to CSV file"""
        # Convert dictionary to DataFrame
        df = pd.DataFrame([data])
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
    
    def process_multiple_resumes(self, pdf_paths: List[str], csv_output_path: str = "all_resumes_data.csv"):
        """Process multiple resumes and save to a single CSV file"""
        all_data = []
        
        for pdf_path in pdf_paths:
            try:
                data = self.parse_resume(pdf_path)
                all_data.append(data)
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")
                continue
        
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(csv_output_path, index=False)
            print(f"Processed {len(all_data)} resumes. Data saved to {csv_output_path}")
        else:
            print("No resumes were successfully processed.")

# Example usage
if __name__ == "__main__":
    # Initialize the advanced converter
    converter = AdvancedResumePDFToCSV()
    
    # Single resume processing
    pdf_file_path = "sample_resume.pdf"  # Change this to your PDF file path
    csv_output_path = "extracted_resume_data.csv"
    
    try:
        print("🚀 Starting Advanced Resume PDF to CSV Conversion")
        print("=" * 60)
        
        # Process single resume
        result = converter.parse_resume(pdf_file_path)
        converter.save_to_csv(result, csv_output_path)
        
        print(f"\n🎉 Successfully converted {pdf_file_path} to {csv_output_path}")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find the PDF file '{pdf_file_path}'")
        print("📝 Creating sample data structure...")
        
        # Create comprehensive sample data
        sample_data = {
            'name': 'Jane Smith',
            'email': 'jane.smith@email.com',
            'phone': '+1-555-987-6543',
            'address': '456 Tech Street, Silicon Valley, CA 94000',
            'linkedin': 'linkedin.com/in/janesmith',
            'github': 'github.com/janesmith',
            'website': 'janesmith.dev',
            'summary': 'Senior Full-Stack Developer with 7+ years of experience in building scalable web applications using modern technologies. Passionate about clean code, user experience, and continuous learning.',
            'education': 'Master of Science in Computer Science | Stanford University | 2016 | Bachelor of Science in Software Engineering | UC Berkeley | 2014',
            'skills': 'Python | JavaScript | React | Node.js | Django | PostgreSQL | MongoDB | AWS | Docker | Kubernetes | Git | Agile | Scrum',
            'experience': 'Senior Software Engineer | TechCorp Inc. | 2020-Present | Led development of microservices architecture | Full-Stack Developer | StartupXYZ | 2017-2020 | Built responsive web applications',
            'certifications': 'AWS Certified Solutions Architect | Google Cloud Professional Developer | Certified Scrum Master',
            'projects': 'E-commerce Platform with React & Node.js | Real-time Chat Application | Machine Learning Price Predictor | Open Source Contribution to Django',
            'languages': 'English (Native) | Spanish (Fluent) | French (Intermediate) | Mandarin (Basic)',
            'achievements': 'Employee of the Year 2022 | Published 3 technical articles | Speaker at PyCon 2023 | Mentored 15+ junior developers',
            'interests': 'Open Source Development | Machine Learning | Photography | Hiking | Chess',
            'references': 'Available upon request'
        }
        
        converter.save_to_csv(sample_data, "sample_advanced_resume_structure.csv")
        print(f"📄 Created comprehensive sample CSV: sample_advanced_resume_structure.csv")
        
        # Example of processing multiple resumes
        print(f"\n💡 To process multiple resumes, use:")
        print("converter.process_multiple_resumes(['resume1.pdf', 'resume2.pdf'], 'all_resumes.csv')")
        
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
