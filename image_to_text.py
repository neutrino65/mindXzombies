import cv2
import pytesseract
import os
import re
from PIL import Image
import argparse
from pathlib import Path
import time
from datetime import datetime

# Try to import pyautogui, but make it optional for WSL environments
try:
    import pyautogui
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    print("Warning: pyautogui not available. Screenshot functionality disabled.")
except Exception as e:
    SCREENSHOT_AVAILABLE = False
    print(f"Warning: Screenshot functionality disabled due to: {str(e)}")
    print("This is common in WSL environments. You can still process existing images.")

class ImageToTextConverter:
    def __init__(self, tesseract_path=None):
        """
        Initialize the converter with optional tesseract path
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Configure tesseract parameters for better text extraction
        self.custom_config = r'--oem 3 --psm 6'
        
        # Ensure images folder exists
        self.images_folder = Path("images")
        self.images_folder.mkdir(exist_ok=True)
        
        # Ensure extracted folder exists
        self.extracted_folder = Path("extracted")
        self.extracted_folder.mkdir(exist_ok=True)
    
    def preprocess_image(self, image_path):
        """
        Preprocess the image to improve OCR accuracy
        """
        try:
            # Read the image
            image = cv2.imread(image_path)
            
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Apply noise reduction
            denoised = cv2.medianBlur(binary, 3)
            
            return denoised
        
        except Exception as e:
            print(f"Error preprocessing image {image_path}: {str(e)}")
            return None
    
    def take_screenshot(self, delay_seconds=3):
        """
        Take a screenshot of the entire screen and save it to images folder
        """
        if not SCREENSHOT_AVAILABLE:
            print("Error: Screenshot functionality is not available in this environment.")
            print("This is common in WSL or headless environments.")
            print("Solutions:")
            print("1. Run this program on Windows directly (not WSL)")
            print("2. Use Windows screenshot tools and save to images/ folder")
            print("3. Use existing images in the images/ folder")
            return None
            
        try:
            print(f"Taking screenshot in {delay_seconds} seconds...")
            print("Please prepare your screen for the screenshot.")
            
            # Countdown
            for i in range(delay_seconds, 0, -1):
                print(f"{i}...", end=" ", flush=True)
                time.sleep(1)
            print("Taking screenshot now!")
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = self.images_folder / filename
            
            # Save screenshot
            screenshot.save(filepath)
            
            # Close the image object to release the file lock
            screenshot.close()
            
            print(f"Screenshot saved to: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            print("This might be due to WSL environment limitations.")
            return None
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from a single image using Tesseract OCR
        """
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image_path)
            
            if processed_image is None:
                return ""
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(processed_image, config=self.custom_config)
            
            # Clean the extracted text
            cleaned_text = self.clean_text(text)
            
            return cleaned_text
            
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return ""
    
    def clean_text(self, text):
        """
        Clean and format the extracted text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might interfere with CSV
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        
        return text
    
    def extract_text_from_multiple_images(self, image_folder):
        """
        Extract text from all images in a folder
        """
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        extracted_data = []
        
        for file_path in Path(image_folder).iterdir():
            if file_path.suffix.lower() in image_extensions:
                print(f"Processing: {file_path.name}")
                text = self.extract_text_from_image(str(file_path))
                
                if text:
                    extracted_data.append({
                        'filename': file_path.name,
                        'extracted_text': text,
                        'text_length': len(text)
                    })
                    print(f"✓ Extracted {len(text)} characters from {file_path.name}")
                else:
                    print(f"✗ No text extracted from {file_path.name}")
        
        return extracted_data
    
    def save_to_text(self, data, output_file):
        """
        Save extracted text data to a text file
        """
        if not data:
            print("No data to save!")
            return
        
        try:
            # Create full path in extracted folder
            output_path = self.extracted_folder / output_file
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(f"=== {item['filename']} ===\n")
                    f.write(f"Text Length: {item['text_length']} characters\n")
                    f.write("-" * 50 + "\n")
                    f.write(item['extracted_text'])
                    f.write("\n\n" + "=" * 80 + "\n\n")
            
            print(f"Text data saved to {output_path}")
            print(f"Total files processed: {len(data)}")
            
        except Exception as e:
            print(f"Error saving to text file: {str(e)}")
    
    def screenshot_and_extract_text(self, delay_seconds=3, output_file="output.txt"):
        """
        Take a screenshot, extract text from it, and save to output file
        """
        try:
            # Take screenshot
            screenshot_path = self.take_screenshot(delay_seconds)
            
            if screenshot_path is None:
                print("Failed to take screenshot.")
                return False
            
            # Extract text from screenshot
            print("Extracting text from screenshot...")
            text = self.extract_text_from_image(screenshot_path)
            
            if text:
                # Save text to output file
                data = [{
                    'filename': Path(screenshot_path).name,
                    'extracted_text': text,
                    'text_length': len(text)
                }]
                
                self.save_to_text(data, output_file)
                print(f"Text extracted and saved to extracted/{output_file}")
                
                # --- NEW FUNCTIONALITY: Delete the original screenshot ---
                try:
                    # Use Path.unlink() for a more robust deletion
                    Path(screenshot_path).unlink()
                    print(f"Original screenshot deleted: {screenshot_path}")
                except Exception as e:
                    print(f"Warning: Could not delete screenshot file: {e}")
                
                return True
            else:
                print("No text extracted from screenshot.")
                return False
            
        except Exception as e:
            print(f"Error in screenshot and text extraction: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Extract text from images using Tesseract OCR and save to text file')
    parser.add_argument('--input', '-i', 
                        help='Input image file or folder containing images')
    parser.add_argument('--output', '-o', default='extracted_text.txt',
                        help='Output text file name (default: extracted_text.txt)')
    parser.add_argument('--tesseract-path', '-t',
                        help='Path to tesseract executable (if not in PATH)')
    parser.add_argument('--screenshot', '-s', action='store_true',
                        help='Take a screenshot and extract text from it')
    parser.add_argument('--delay', type=int, default=3,
                        help='Delay in seconds before taking screenshot (default: 3)')
    
    args = parser.parse_args()
    
    try:
        # Initialize converter
        converter = ImageToTextConverter(args.tesseract_path)
        
        # Handle screenshot mode
        if args.screenshot:
            if not SCREENSHOT_AVAILABLE:
                print("Error: Screenshot mode is not available in this environment.")
                print("Please use --input to process existing images instead.")
                return
            
            print("Screenshot mode activated!")
            success = converter.screenshot_and_extract_text(
                delay_seconds=args.delay, 
                output_file=args.output
            )
            if success:
                print(f"Screenshot text extraction completed successfully!")
                print(f"Text saved to: extracted/{args.output}")
            return
        
        # Handle regular image processing
        if not args.input:
            print("Error: Please provide --input to process existing images")
            if not SCREENSHOT_AVAILABLE:
                print("Note: Screenshot mode is not available in this environment.")
            return
        
        input_path = Path(args.input)
        
        if input_path.is_file():
            # Single image file
            print(f"Processing single image: {input_path.name}")
            text = converter.extract_text_from_image(str(input_path))
            
            if text:
                data = [{
                    'filename': input_path.name,
                    'extracted_text': text,
                    'text_length': len(text)
                }]
                
                converter.save_to_text(data, args.output)
                print(f"Text saved to: extracted/{args.output}")
            else:
                print("No text extracted from the image.")
        
        elif input_path.is_dir():
            # Folder containing images
            print(f"Processing images in folder: {input_path}")
            data = converter.extract_text_from_multiple_images(str(input_path))
            
            if data:
                converter.save_to_text(data, args.output)
                print(f"Text saved to: extracted/{output_file}")
            else:
                print("No text extracted from any images.")
        
        else:
            print(f"Error: {args.input} is not a valid file or directory.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nMake sure you have:")
        print("1. Tesseract OCR installed on your system.")
        print("2. Required dependencies installed: pip install opencv-python pytesseract pillow")
        if not SCREENSHOT_AVAILABLE:
            print("3. For screenshot functionality: pip install pyautogui (not available in WSL)")
        else:
            print("3. For screenshot functionality: pip install pyautogui")

if __name__ == "__main__":
    print("Tesseract OCR Image to Text Extractor")
    print("=" * 50)
    
    # Check if running interactively
    try:
        import sys
        if len(sys.argv) > 1:
            main()
        else:
            print("Running in interactive mode...")
            
            # Initialize converter
            converter = ImageToTextConverter()
            
            # Ask user what they want to do
            print("\nWhat would you like to do?")
            print("1. Process existing images")
            
            if SCREENSHOT_AVAILABLE:
                print("2. Take a screenshot and extract text")
                choice = input("Enter your choice (1 or 2): ").strip()
            else:
                print("2. Take a screenshot and extract text (NOT AVAILABLE in this environment)")
                choice = input("Enter your choice (1): ").strip()
                if choice == "2":
                    print("Screenshot functionality is not available in WSL environment.")
                    print("Please choose option 1 to process existing images.")
                    choice = "1"
            
            if choice == "2":
                # Screenshot mode
                delay = input("Enter delay in seconds before screenshot (default: 3): ").strip()
                if not delay:
                    delay = 3
                else:
                    delay = int(delay)
                
                output_file = input("Enter output text filename (default: output.txt): ").strip()
                if not output_file:
                    output_file = "output.txt"
                
                print("Screenshot mode activated!")
                success = converter.screenshot_and_extract_text(
                    delay_seconds=delay, 
                    output_file=output_file
                )
                if success:
                    print("Screenshot text extraction completed successfully!")
                    print(f"Text saved to: extracted/{output_file}")
            
            elif choice == "1":
                # Regular image processing mode
                input_path = input("Enter image file path or folder path: ").strip()
                output_file = input("Enter output text filename (default: extracted_text.txt): ").strip()
                
                if not output_file:
                    output_file = "extracted_text.txt"
                
                # Check if input is a file or folder
                input_path_obj = Path(input_path)
                
                if input_path_obj.is_file():
                    print(f"Processing single image: {input_path_obj.name}")
                    text = converter.extract_text_from_image(str(input_path_obj))
                    
                    if text:
                        data = [{
                            'filename': input_path_obj.name,
                            'extracted_text': text,
                            'text_length': len(text)
                        }]
                        converter.save_to_text(data, output_file)
                        print(f"Text saved to: extracted/{output_file}")
                    else:
                        print("No text extracted from the image.")
                
                elif input_path_obj.is_dir():
                    print(f"Processing images in folder: {input_path_obj}")
                    data = converter.extract_text_from_multiple_images(str(input_path_obj))
                    
                    if data:
                        converter.save_to_text(data, output_file)
                        print(f"Text saved to: extracted/{output_file}")
                    else:
                        print("No text extracted from any images.")
                
                else:
                    print(f"Error: {input_path} is not a valid file or directory.")
            else:
                if SCREENSHOT_AVAILABLE:
                    print("Invalid choice. Please enter 1 or 2.")
                else:
                    print("Invalid choice. Please enter 1.")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nMake sure you have the required dependencies installed:")
        print("pip install opencv-python pytesseract pillow")
        if not SCREENSHOT_AVAILABLE:
            print("Note: Screenshot functionality not available in WSL environment")
        print("\nAlso ensure Tesseract OCR is installed on your system.")
        print("\nInstallation instructions:")
        print("Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("macOS: brew install tesseract")
        print("Linux: sudo apt-get install tesseract-ocr")
