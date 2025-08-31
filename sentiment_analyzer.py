import requests
import os
import sys

# Important: This API key will be provided automatically in the Canvas environment.
# Do not modify this line.
API_KEY = "" # The API key for Gemini API
# Using gemini-pro which has wider regional availability
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + API_KEY

def analyze_text_with_gemini(text_to_analyze):
    """
    Sends text to the Gemini API for sentiment analysis of negative or depressive thoughts.
    
    Args:
        text_to_analyze (str): The text content to be analyzed.
        
    Returns:
        str: The sentiment analysis result as a simple "True" or "False" string.
    """
    # Check if the text is empty or too short before making the API call
    if not text_to_analyze or len(text_to_analyze.strip()) < 5:
        return "negative behavioral  False"

    # The system instruction guides the model's persona and task.
    system_instruction = "Your only task is to analyze text for negative thinking, depressive behavior, or violence. Respond with only a single word: 'True' if the text contains any of these concepts, and 'False' if it does not. Do not provide any other text, explanation, or punctuation."

    # The user prompt contains the text to be analyzed.
    user_prompt = f"Analyze the following text for negative thinking, depressive behavior, or violence: '{text_to_analyze}'"

    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # Parse the JSON response
        response_data = response.json()
        
        # Extract the model's response text
        generated_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # We expect a single-word response, either 'True' or 'False'
        if generated_text.strip().lower() == "true":
            return "negative behavioral  True"
        else:
            return "negative behavioral  False"

    except requests.exceptions.RequestException as e:
        if "403" in str(e):
            print("Error: The API key is invalid or unauthorized for this model.")
            print("Please ensure your key is correct and the model is available in your region.")
            print("You may also try a different model, such as 'gemini-pro'.")
        else:
            print(f"An error occurred during the API request: {e}")
        return "An error occurred"
    except (KeyError, IndexError) as e:
        print(f"Failed to parse the API response: {e}")
        print("Raw response:", response.text)
        return "An error occurred"

def main():
    """
    Main function to read the text from a command-line argument and analyze it.
    """
    # Check if a command-line argument was provided
    if len(sys.argv) < 2:
        print("Error: No text provided as a command-line argument.")
        return

    # The text is the first command-line argument
    text_to_analyze = sys.argv[1]

    if not text_to_analyze.strip():
        print("The provided text is empty. No analysis to perform.")
        return

    print("Analyzing the text...")
    print("---")
    print(text_to_analyze.strip())
    print("---")
    
    result = analyze_text_with_gemini(text_to_analyze)
    print(result)

if __name__ == "__main__":
    main()

