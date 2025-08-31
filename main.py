import subprocess
import time
import os
import sys
import ctypes  # New import for the pop-up alert

def run_image_to_text():
    """
    Executes the image_to_text.py script to take a screenshot and returns the extracted text.
    """
    print("Running image_to_text.py to capture and extract text...")
    try:
        # Run image_to_text.py with specific arguments. The output is a string.
        result = subprocess.run(
            [sys.executable, "image_to_text.py", "--screenshot", "--delay", "1", "--output", "output.txt"],
            capture_output=True,
            text=True,
            check=True
        )
        print("Image to text extraction completed.")
        
        # The script prints a lot of info to stdout, we need to parse it for the actual text
        # The script saves text to 'extracted/output.txt' and prints the path
        # We can look for that line and then read the file
        output_path_line = [line for line in result.stdout.splitlines() if "Text data saved to extracted" in line]
        if output_path_line:
            # The line is something like "Text data saved to extracted\output.txt"
            output_file_name = output_path_line[0].split()[-1].replace("\\", "/").split("/")[-1]
            file_path = os.path.join("extracted", output_file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
                os.remove(file_path) # Clean up the temporary file immediately
                return extracted_text
            else:
                print(f"Warning: Extracted file not found at {file_path}")
                return None
        else:
            print("Warning: Could not locate the extracted text file path in the output.")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error executing image_to_text.py: {e}")
        print(e.stdout)
        print(e.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred during image-to-text processing: {e}")
        return None

def run_sentiment_analysis(text_to_analyze):
    """
    Executes the sentiment_analyzer.py script with the extracted text.
    Returns: True if negative behavior is detected, False otherwise.
    """
    if not text_to_analyze:
        print("No text to analyze. Skipping sentiment analysis.")
        return False
        
    print("Running sentiment_analyzer.py to analyze text...")
    try:
        # Pass the extracted text as a command-line argument to sentiment_analyzer.py
        result = subprocess.run(
            [sys.executable, "sentiment_analyzer.py", text_to_analyze],
            capture_output=True,
            text=True,
            check=False
        )
        print("Sentiment analysis completed.")
        
        # The analyzer should only print True or False
        sentiment_output = result.stdout.strip()
        
        print(f"Result from analyzer: {sentiment_output}")
        if result.stderr:
            print("--- Sentiment Analysis Error Output ---")
            print(result.stderr)
            print("--- End Error Output ---")
        
        # Check if the output indicates a negative behavior
        if "negative behavioral  True" in sentiment_output:
            return True
        return False
        
    except Exception as e:
        print(f"An error occurred during sentiment analysis: {e}")
        return False

def show_popup_alert():
    """
    Shows a pop-up alert on Windows 11 using ctypes.
    The pop-up will appear on top of all other applications.
    """
    # Define a warning message and a title for the pop-up
    message = "Potential negative thought detected. Self-awareness is key to managing mental health. Acknowledge the thought and refocus your attention."
    title = "Behavioral Alert"
    
    # Flags for the message box style:
    # MB_ICONWARNING (0x30) - Yellow warning sign
    # MB_SYSTEMMODAL (0x1000) - Makes the dialog box a system-modal dialog,
    # which means it will stay on top of all other windows.
    # The combination `0x1030` ensures the popup is on top and has a warning icon.
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x1030)

def main():
    """
    Main loop to orchestrate the entire process.
    """
    while True:
        print("--- Starting new cycle ---")
        
        # Step 1: Run the image-to-text script and get the text
        extracted_text = run_image_to_text()
        
        # Step 2: Run the sentiment analysis script with the extracted text
        is_negative = run_sentiment_analysis(extracted_text)
        
        # Step 3: Show the pop-up alert if negative behavior is detected
        if is_negative:
            show_popup_alert()
            
        print("--- Cycle complete. Waiting for 10 seconds... ---")
        time.sleep(10)

if __name__ == "__main__":
    main()
