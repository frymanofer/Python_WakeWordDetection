from PyPDF2 import PdfReader

# Paths of the uploaded PDF files
file_paths = [
]

# Function to count the number of pages in a PDF file
def count_pdf_pages(file_path):
    try:
        reader = PdfReader(file_path)
        return len(reader.pages)
    except Exception as e:
        return f"Error: {e}"

# Counting the pages in each file
page_counts = {file_path: count_pdf_pages(file_path) for file_path in file_paths}
page_counts

