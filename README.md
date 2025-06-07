# 📄 Resume PDF to CSV Converter 🚀

Transform your resume PDFs into structured CSV data with this powerful Python tool! Perfect for recruiters, HR professionals, or anyone looking to digitize and analyze resume data efficiently.

## ✨ Features

- 🔍 Smart text extraction from PDF resumes
- 📱 Contact information detection (email, phone, LinkedIn, GitHub)
- 🎯 Section-based content parsing
- 📊 Clean CSV output format
- 🎨 Beautiful and organized data structure

## 🛠️ Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/resume-pdf-to-csv.git
cd resume-pdf-to-csv
```

2. Install the required dependencies:
```bash
cd scripts
pip install -r requirements.txt
```

## 🚀 Quick Start

Convert a single resume:
```bash
python run_converter.py "path/to/your/resume.pdf" "output.csv"
```

Process multiple resumes:
```python
from advanced_resume_parser import AdvancedResumePDFToCSV

converter = AdvancedResumePDFToCSV()
resumes = ["resume1.pdf", "resume2.pdf", "resume3.pdf"]
converter.process_multiple_resumes(resumes, "all_resumes.csv")
```


## 🎯 Example Usage

```python
# Single resume conversion
python run_converter.py "John_Doe_Resume.pdf" "john_doe_data.csv"

# Multiple resume processing
python run_converter.py "resumes/*.pdf" "all_candidates.csv"
```

## 🛠️ Customization

The `AdvancedResumePDFToCSV` class is highly customizable. You can:
- Modify section headers
- Add new data fields
- Customize output format
- Adjust parsing rules

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- PyPDF2 for PDF processing
- pandas for data manipulation
- NLTK for text processing
- The open-source community

## 🎨 Made with ❤️

Built with Python and a passion for making resume processing easier!

---
⭐ Star this repository if you find it useful! 
