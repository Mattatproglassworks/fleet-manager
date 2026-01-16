"""
AI-powered document processing for maintenance records
Extracts vehicle information, maintenance details, dates, mileage, and costs from uploaded documents
"""
import os
import re
from datetime import datetime
from typing import Dict, Optional, List
import PyPDF2
from PIL import Image
import pytesseract
from io import BytesIO

# Try to import OpenAI - if not available, will use fallback parsing
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class DocumentProcessor:
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the document processor with optional OpenAI API key"""
        self.openai_client = None
        if OPENAI_AVAILABLE and openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_image(self, file_content: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(BytesIO(file_content))
            # Improve OCR accuracy with config options
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=custom_config)
            print(f"📜 FULL OCR TEXT:\n{text}\n{'='*50}")
            return text
        except pytesseract.TesseractNotFoundError:
            raise Exception("Tesseract OCR is not installed. Please install Tesseract from https://github.com/tesseract-ocr/tesseract and add it to your system PATH. For Windows: Download the installer from https://github.com/UB-Mannheim/tesseract/wiki")
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    def extract_text(self, filename: str, file_content: bytes) -> str:
        """Extract text from document based on file type"""
        ext = filename.lower().rsplit('.', 1)[1] if '.' in filename else ''
        
        if ext == 'pdf':
            return self.extract_text_from_pdf(file_content)
        elif ext in ['jpg', 'jpeg', 'png']:
            return self.extract_text_from_image(file_content)
        else:
            return ""
    
    def parse_with_ai(self, text: str, vehicles: List[Dict]) -> Dict:
        """Use OpenAI to parse maintenance document and extract structured data"""
        if not self.openai_client:
            return self.parse_with_regex(text, vehicles)
        
        try:
            # Create a list of known vehicles for context
            vehicle_context = "\n".join([
                f"- {v['year']} {v['make']} {v['model']} (VIN: {v['vin']}, License: {v['license_plate']})"
                for v in vehicles
            ])
            
            prompt = f"""You are analyzing a vehicle maintenance document. Extract the following information and return it as JSON:

Known vehicles in the system:
{vehicle_context}

Document text:
{text}

Extract and return JSON with these fields (use null if not found):
{{
    "vehicle_identifier": "VIN, license plate, OR year+make+model (e.g., '2017 Ford Transit', '2022 Mercedes Metris'). IMPORTANT: Extract the full vehicle description including year, make, and model even if no VIN/plate is visible.",
    "maintenance_type": "Type of service (Oil Change, Tire Rotation, Brake Service, etc.)",
    "description": "Detailed description of work performed",
    "service_date": "Date in YYYY-MM-DD format",
    "mileage": "Mileage as integer (just the number)",
    "cost": "Total cost as decimal (just the number, no $ sign)",
    "provider": "Name of service provider/shop",
    "next_service_mileage": "Recommended next service mileage if mentioned"
}}

IMPORTANT: For vehicle_identifier, if you can't find VIN or license plate, extract the year, make, and model (e.g., '2017 Ford Transit') to match against the known vehicles.
Be precise and only extract information that is clearly stated in the document."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise data extraction assistant. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI parsing error: {e}")
            return self.parse_with_regex(text, vehicles)
    
    def parse_with_regex(self, text: str, vehicles: List[Dict]) -> Dict:
        """Fallback parser using regex patterns"""
        result = {
            "vehicle_identifier": None,
            "maintenance_type": None,
            "description": None,
            "service_date": None,
            "mileage": None,
            "cost": None,
            "provider": None,
            "next_service_mileage": None
        }
        
        # Extract VIN (17 characters alphanumeric)
        vin_match = re.search(r'\b[A-HJ-NPR-Z0-9]{17}\b', text, re.IGNORECASE)
        if vin_match:
            result["vehicle_identifier"] = vin_match.group()
        
        # Extract license plate patterns
        if not result["vehicle_identifier"]:
            license_patterns = [
                r'\b[A-Z]{2,3}[0-9]{3,4}\b',
                r'\b[0-9]{1,3}[A-Z]{2,3}[0-9]{1,3}\b'
            ]
            for pattern in license_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result["vehicle_identifier"] = match.group()
                    break
        
        # Extract year/make/model if no VIN/plate found
        if not result["vehicle_identifier"]:
            # Priority 1: Look for "Vehicle:" label (common on receipts)
            # Handle OCR errors like "5018" for "2018" by matching any 4-digit number
            vehicle_label = re.search(r'Vehicle\s*:\s*(\d{4})\s+([A-Za-z]+)\s+([A-Za-z]+)', text, re.IGNORECASE)
            if vehicle_label:
                year_ocr = vehicle_label.group(1)
                make = vehicle_label.group(2)
                model = vehicle_label.group(3)
                # Convert OCR-mangled years: 5018->2018, 7017->2017, etc.
                if year_ocr.startswith('5') or year_ocr.startswith('7') or year_ocr.startswith('4'):
                    year_fixed = '20' + year_ocr[2:]
                    print(f"🔧 OCR year fix: {year_ocr} -> {year_fixed}")
                    result["vehicle_identifier"] = f"{year_fixed} {make} {model}"
                else:
                    result["vehicle_identifier"] = vehicle_label.group().replace('Vehicle:', '').replace('Vehicle :', '').strip()
            else:
                # Priority 2: Standard year + make + model pattern
                year_make_model = re.search(r'(19[9][0-9]|20[0-3][0-9])\s+([A-Za-z]+)\s+([A-Za-z][a-z]+(?:\s+[A-Z0-9][a-z0-9]+)*)', text, re.IGNORECASE)
                if year_make_model:
                    result["vehicle_identifier"] = year_make_model.group().strip()
                else:
                    # Priority 3: Just make and model
                    make_model = re.search(r'\b(Ford|Mercedes|Toyota|Chevrolet|GMC|RAM|Dodge|Honda|Nissan)\s+([A-Za-z][a-z]+(?:\s+[A-Z0-9][a-z0-9]+)*)', text, re.IGNORECASE)
                    if make_model:
                        result["vehicle_identifier"] = make_model.group().strip()
        
        print(f"🚗 Extracted vehicle identifier: {result.get('vehicle_identifier')}")
        
        # Extract mileage
        mileage_patterns = [
            r'(?:mileage|odometer|miles?)[\s:]+([0-9,]+)',
            r'([0-9,]+)[\s]+(?:miles?|mi\b)'
        ]
        for pattern in mileage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["mileage"] = int(match.group(1).replace(',', ''))
                break
        
        # Extract cost/total - improved patterns to get the TOTAL cost
        cost_patterns = [
            # Priority 1: Look for "total" or "amount due" specifically
            r'(?:total|grand\s*total|amount\s*due|total\s*due|balance|total\s*cost)[\s:$]*\$?\s?([0-9,]+\.[0-9]{2})',
            # Priority 2: Dollar amounts at end of lines (often the total)
            r'\$\s?([0-9,]+\.[0-9]{2})\s*$',
            # Priority 3: Any dollar amount
            r'\$\s?([0-9,]+\.[0-9]{2})',
            # Priority 4: Decimals that look like money
            r'\b([0-9,]+\.[0-9]{2})\b'
        ]
        
        all_costs = []
        for pattern in cost_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                for m in matches:
                    try:
                        cost_val = float(m.replace(',', ''))
                        if 1.0 <= cost_val <= 50000:  # Reasonable maintenance cost range
                            all_costs.append(cost_val)
                    except:
                        pass
        
        if all_costs:
            # Use the largest cost as the total (usually the final amount)
            result["cost"] = max(all_costs)
            print(f"💰 Found costs: {all_costs}, using max: {result['cost']}")
        
        # Extract dates
        date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    # Try to parse the date
                    date_str = match.group(1)
                    for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            result["service_date"] = parsed_date.strftime('%Y-%m-%d')
                            break
                        except:
                            continue
                    if result["service_date"]:
                        break
                except:
                    pass
        
        # Detect maintenance type from common keywords
        maintenance_keywords = {
            "Smog Check": ["smog", "smog check", "smog test", "smog inspection", "emissions"],
            "Oil Change": ["oil change", "oil service", "lube"],
            "Tire Rotation": ["tire rotation", "rotate tires"],
            "Brake Service": ["brake", "brakes", "brake pad", "brake service"],
            "Inspection": ["inspection", "state inspection", "safety check"],
            "Tune-Up": ["tune-up", "tune up", "tuneup"],
            "Transmission": ["transmission", "trans service"],
            "Battery": ["battery", "battery replacement"],
            "Alignment": ["alignment", "wheel alignment"],
        }
        
        text_lower = text.lower()
        for service_type, keywords in maintenance_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                result["maintenance_type"] = service_type
                break
        
        if not result["maintenance_type"]:
            result["maintenance_type"] = "General Service"
        
        return result
    
    def match_vehicle(self, identifier: Optional[str], vehicles: List[Dict], mileage: Optional[int] = None) -> Optional[Dict]:
        """Match extracted identifier to a vehicle in the system"""
        if not identifier:
            return None
        
        identifier = identifier.upper()
        
        # Track partial matches for fallback
        partial_matches = []
        
        for vehicle in vehicles:
            # Check VIN match (highest priority)
            if vehicle['vin'] and vehicle['vin'].upper() in identifier:
                return vehicle
            
            # Check license plate match (high priority)
            if vehicle['license_plate'] and vehicle['license_plate'].upper() in identifier:
                return vehicle
            
            # Check for year + make + model match (exact combination)
            year_str = str(vehicle['year'])
            make_upper = vehicle['make'].upper()
            model_upper = vehicle['model'].upper()
            
            # Split model into parts for partial matching (e.g., "Transit Connect" -> ["TRANSIT", "CONNECT"])
            model_parts = model_upper.split()
            
            # Count how many components match
            match_score = 0
            
            # Check for year - also handle OCR errors like "5018" for "2018"
            if year_str in identifier:
                match_score += 4  # Exact year match is very important
            else:
                # Check for OCR-mangled years (e.g., 5018 = 2018, 7017 = 2017)
                for ocr_year in [f"5{year_str[1:]}", f"7{year_str[1:]}", f"4{year_str[1:]}"]:
                    if ocr_year in identifier:
                        match_score += 3  # OCR year match
                        print(f"🔧 OCR year correction: {ocr_year} -> {year_str}")
                        break
            
            if make_upper in identifier:
                match_score += 3  # Make is very important
            
            # Check if any significant part of the model matches
            # For models like "Transit Connect", if "TRANSIT" matches, that's good
            for part in model_parts:
                if len(part) >= 4 and part in identifier:  # Only check significant words (4+ chars)
                    match_score += 3
                    break  # One significant match is enough
            
            # Bonus points if mileage is close to vehicle's current mileage
            if mileage and vehicle.get('current_mileage'):
                mileage_diff = abs(mileage - vehicle['current_mileage'])
                if mileage_diff < 5000:  # Within 5000 miles
                    match_score += 2
                    print(f"📍 Mileage proximity bonus for {vehicle['year']} {vehicle['make']} {vehicle['model']}: doc={mileage}, vehicle={vehicle['current_mileage']}")
            
            # If we have make and at least part of model, that's a good match
            if match_score >= 6:  # Make (3) + Model part (3) = 6
                partial_matches.append((match_score, vehicle))
                print(f"📊 Match candidate: {vehicle['year']} {vehicle['make']} {vehicle['model']} - score: {match_score}")
        
        # Return the best partial match if we found any
        if partial_matches:
            # Sort by score (highest first) and return best match
            partial_matches.sort(key=lambda x: x[0], reverse=True)
            best_match = partial_matches[0][1]
            print(f"🏆 Best match: {best_match['year']} {best_match['make']} {best_match['model']} with score {partial_matches[0][0]}")
            return best_match
        
        return None
    
    def process_document(self, filename: str, file_content: bytes, vehicles: List[Dict], 
                        preselected_vehicle_id: Optional[int] = None) -> Dict:
        """Main processing pipeline for uploaded documents"""
        # Extract text from document
        text = self.extract_text(filename, file_content)
        
        print(f"📄 Extracted text length: {len(text) if text else 0} characters")
        if text:
            print(f"📄 First 200 chars: {text[:200]}")
        
        if not text or len(text.strip()) < 50:
            return {
                "success": False,
                "error": "Could not extract sufficient text from document. Please ensure the document is clear and readable."
            }
        
        # Parse document with AI or regex
        parsed_data = self.parse_with_ai(text, vehicles)
        print(f"🔍 Parsed data: {parsed_data}")
        
        # Match to vehicle
        matched_vehicle = None
        if preselected_vehicle_id:
            matched_vehicle = next((v for v in vehicles if v['id'] == preselected_vehicle_id), None)
            print(f"✅ Using preselected vehicle: {matched_vehicle}")
        
        if not matched_vehicle and parsed_data.get('vehicle_identifier'):
            print(f"🔎 Attempting to match vehicle with identifier: {parsed_data.get('vehicle_identifier')}")
            matched_vehicle = self.match_vehicle(parsed_data['vehicle_identifier'], vehicles, parsed_data.get('mileage'))
            if matched_vehicle:
                print(f"✅ Matched vehicle: {matched_vehicle['year']} {matched_vehicle['make']} {matched_vehicle['model']}")
            else:
                print(f"❌ No vehicle matched")
        
        if not matched_vehicle:
            return {
                "success": False,
                "error": "Could not identify which vehicle this document belongs to. Please select a vehicle manually.",
                "extracted_data": parsed_data,
                "raw_text": text[:500]  # First 500 chars for debugging
            }
        
        # Validate extracted data
        if not parsed_data.get('maintenance_type'):
            return {
                "success": False,
                "error": "Could not determine the type of maintenance performed.",
                "extracted_data": parsed_data,
                "vehicle": matched_vehicle
            }
        
        return {
            "success": True,
            "vehicle": matched_vehicle,
            "maintenance_type": parsed_data.get('maintenance_type'),
            "description": parsed_data.get('description') or f"Imported from {filename}",
            "service_date": parsed_data.get('service_date'),
            "mileage": parsed_data.get('mileage'),
            "cost": parsed_data.get('cost'),
            "provider": parsed_data.get('provider'),
            "next_service_mileage": parsed_data.get('next_service_mileage'),
            "raw_text": text[:500]
        }
