import sys
from advanced_resume_parser import AdvancedResumePDFToCSV

def main():
    # Check if PDF file path is provided
    if len(sys.argv) < 2:
        print("Usage: python run_converter.py <pdf_file_path> [output_csv_path]")
        print("If output_csv_path is not provided, it will default to 'extracted_resume_data.csv'")
        sys.exit(1)
    
    # Get PDF file path
    pdf_path = sys.argv[1]
    
    # Get output CSV path (optional)
    output_path = sys.argv[2] if len(sys.argv) > 2 else "extracted_resume_data.csv"
    
    try:
        # Create converter instance
        converter = AdvancedResumePDFToCSV()
        
        # Parse resume and save to CSV
        data = converter.parse_resume(pdf_path)
        converter.save_to_csv(data, output_path)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
