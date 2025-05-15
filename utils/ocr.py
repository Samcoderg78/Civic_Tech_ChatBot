def validate_vin(vin):
    """Validate VIN using the standard VIN format rules"""
    # Basic VIN validation - 17 characters, alphanumeric only (excluding I, O, Q)
    if not vin or len(vin) != 17:
        return False
    
    # VIN should only contain alphanumeric characters (excluding I, O, Q)
    valid_chars = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
    return all(char in valid_chars for char in vin.upper())

def extract_vin(image_url):
    """Extract VIN from image using OCR"""
    try:
        # Download and open image
        image_data = download_image(image_url)
        img = np.array(Image.open(image_data))
        
        # Preprocess image
        processed = preprocess_image(img)
        
        # Apply OCR
        ocr_text = pytesseract.image_to_string(processed, config='--psm 11')
        
        # Process OCR text to find potential VINs
        text_lines = ocr_text.split('\n')
        for line in text_lines:
            # Clean the line
            cleaned = re.sub(r'[^A-Z0-9]', '', line.upper())
            
            # Look for 17-character sequences that could be VINs
            potential_vins = re.findall(r'[A-HJ-NPR-Z0-9]{17}', cleaned)
            
            for vin in potential_vins:
                if validate_vin(vin):
                    return vin
        
        # If no valid VIN was found in the OCR text, try a different approach
        # This uses a more focused OCR with custom configuration
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHJKLMNPRSTUVWXYZ0123456789'
        ocr_text = pytesseract.image_to_string(processed, config=custom_config)
        
        # Clean and search again
        cleaned = re.sub(r'[^A-Z0-9]', '', ocr_text.upper())
        potential_vins = re.findall(r'[A-HJ-NPR-Z0-9]{17}', cleaned)
        
        for vin in potential_vins:
            if validate_vin(vin):
                return vin
                
        return None
        
    except Exception as e:
        print(f"Error extracting VIN: {str(e)}")
        return None