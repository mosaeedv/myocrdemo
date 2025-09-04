
import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from PyPDF2 import PdfMerger
from io import BytesIO
from website.models import PdfData
from website import db

# ---------- Config ----------
tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"
languages = "eng+fas"   # English + Persian

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


# ---------- Step 0: Get PDF from database ----------
def process_pdf_from_db(pdf_id):
    pdf_record = PdfData.query.get(pdf_id)
    if not pdf_record:
        print(f"❌ PDF with id {pdf_id} not found in database.")
        return None
    pdf_path = os.path.join("website/static/uploads", pdf_record.filename)
    if not os.path.isfile(pdf_path):
        print(f"❌ File {pdf_path} not found.")
        return None
    file_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_folder = os.path.join(os.path.dirname(pdf_path), "output")
    os.makedirs(output_folder, exist_ok=True)
    output_prefix = file_name


    # ---------- Step 1: Convert PDF to PNG ----------
    print("📄 Converting PDF to images...")
    pages = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    png_files = []
    for i, page in enumerate(pages):
        png_path = os.path.join(output_folder, f"{output_prefix}_page_{i+1}.png")
        page.save(png_path, "PNG")
        png_files.append(png_path)
        print(f"✅ Saved PNG: {png_path}")

    # ---------- Step 2: OCR each PNG and save text ----------
    print("🔍 Running OCR on images...")
    all_text = ""
    for i, png_path in enumerate(png_files):
        text = pytesseract.image_to_string(Image.open(png_path), lang=languages)
        all_text += f"\n\n--- Page {i+1} ---\n\n{text}"

    # Save OCR result to database
    pdf_record.ocr_text = all_text
    db.session.commit()
    print(f"✅ OCR result saved to database for PDF id {pdf_id}")

    # ---------- Step 3: Create a searchable PDF ----------
    print("📕 Creating searchable PDF...")
    searchable_pdf_path = os.path.join(output_folder, f"{output_prefix}_searchable.pdf")
    pdf_bytes_list = []
    for png_path in png_files:
        pdf_bytes = pytesseract.image_to_pdf_or_hocr(Image.open(png_path), lang=languages, extension='pdf')
        pdf_bytes_list.append(pdf_bytes)
    merger = PdfMerger()
    for pdf_bytes in pdf_bytes_list:
        merger.append(BytesIO(pdf_bytes))
    merger.write(searchable_pdf_path)
    merger.close()
    print(f"✅ Saved searchable PDF: {searchable_pdf_path}")
    return all_text
