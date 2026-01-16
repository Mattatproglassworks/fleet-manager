# AI Document Processing Feature

## Overview
This feature allows you to upload maintenance documents (receipts, invoices, service reports) and automatically extract all the information using AI.

## What It Does
The system automatically extracts:
- **Vehicle identification** (VIN, license plate, or vehicle description)
- **Maintenance type** (Oil Change, Brake Service, Tire Rotation, etc.)
- **Service date**
- **Mileage** at time of service
- **Cost** of service
- **Service provider** name
- **Next service mileage** (if mentioned)

## How to Use

### 1. Set Up (Optional but Recommended)
For best results, add your OpenAI API key:

1. Copy `.env.example` to `.env`
2. Get an API key from https://platform.openai.com/api-keys
3. Add it to `.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

**Note:** The system will work without an API key using regex pattern matching, but AI processing is more accurate.

### 2. Upload a Document
1. Click "Upload Document" in the navigation
2. Select a PDF, JPG, or PNG file (max 10MB)
3. Optionally select a vehicle (AI will verify it matches the document)
4. Click "Process Document with AI"

### 3. Review and Confirm
The system will:
- Extract text from the document
- Parse all maintenance information
- Match it to the correct vehicle
- Create a maintenance record automatically
- Update the vehicle's mileage if higher

## Supported Documents
- Service receipts
- Maintenance invoices
- Oil change records
- Inspection reports
- Repair bills
- Any document with vehicle service information

## Tips for Best Results
- Ensure documents are clear and readable
- Include the full receipt/invoice
- Make sure VIN or license plate is visible
- Document should show date, mileage, and services performed

## Technical Details

### With OpenAI API (Recommended)
- Uses GPT-4o-mini for intelligent text extraction
- Understands context and can handle various document formats
- More accurate vehicle matching
- Better at identifying service types

### Without OpenAI API (Fallback)
- Uses regex pattern matching
- Extracts VINs, license plates, dates, mileage, costs
- Works for standard formatted documents
- Free to use, no API costs

### Supported File Types
- PDF (`.pdf`)
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)

### Processing Steps
1. **Text Extraction**
   - PDFs: Uses PyPDF2
   - Images: Uses Tesseract OCR (pytesseract)

2. **Information Parsing**
   - With AI: OpenAI API analyzes text and extracts structured data
   - Without AI: Regex patterns match common formats

3. **Vehicle Matching**
   - Matches VIN, license plate, or vehicle description
   - Verifies against your fleet database

4. **Record Creation**
   - Creates MaintenanceRecord with all extracted data
   - Updates vehicle mileage if needed
   - Links to correct vehicle automatically

## Dependencies
- `openai` - For AI-powered extraction
- `pytesseract` - For OCR (image text extraction)
- `PyPDF2` - For PDF text extraction
- `Pillow` - For image processing
- `pdf2image` - For PDF to image conversion
- `python-dotenv` - For environment variables

## Installation
All dependencies are included in `requirements.txt`. Install with:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### "Could not extract sufficient text"
- Make sure document is clear and not too blurry
- Try uploading a higher resolution scan
- Ensure document is not password protected

### "Could not identify which vehicle"
- Manually select the vehicle in the form
- Ensure VIN or license plate is visible in document
- Check that vehicle exists in your fleet database

### OCR Not Working (Images)
- Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- Windows: Download installer and add to PATH
- Mac: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

## Future Enhancements
- Batch processing multiple documents
- Email integration (forward receipts to email)
- Mobile app for scanning documents on the go
- Historical document analysis
- Automatic categorization and tagging
