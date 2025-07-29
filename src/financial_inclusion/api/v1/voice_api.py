from fastapi import APIRouter, HTTPException,UploadFile,File,HTTPException
from financial_inclusion.core.logging import logging
import google.generativeai as genai
import os
import base64

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/voice")

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

@app.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):
    """
    Accepts an audio file and transcribes it to text using the Gemini API.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file was uploaded.")

    # Supported MIME types for the Gemini API
    supported_mime_types = [
        "audio/wav", "audio/mpeg", "audio/webm", "audio/ogg", "audio/flac", "audio/mp4"
    ]
    if file.content_type not in supported_mime_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {file.content_type}. Please use one of: {', '.join(supported_mime_types)}",
        )

    try:
        # We use the 'gemini-1.5-pro-latest' model which is excellent for transcription
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        # Read the file content
        audio_data = await file.read()

        # Upload the file to the Generative AI service
        audio_file = genai.upload_file(
            path=audio_data,
            display_name="user-recording",
            mime_type=file.content_type
        )
        
        # A simple prompt for transcription is effective
        prompt = "Transcribe this audio."
        
        # Generate content using the model
        response = model.generate_content([prompt, audio_file])

        # Check if the response contains text
        if not response.text:
             raise HTTPException(status_code=500, detail="Transcription failed. The model did not return any text.")

        return {"text": response.text}

    except Exception as e:
        print(f"An error occurred: {e}") # For logging/debugging
        raise HTTPException(status_code=500, detail="An error occurred during the transcription process.")

async def audio_to_base64(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()

        base64_encoded_bytes = base64.b64encode(audio_bytes)

        base64_encoded_string = base64_encoded_bytes.decode('utf-8')

        return {
            "base64": base64_encoded_string,
            "mimeType": file.content_type
        }
    except Exception as e:
        logger.error(e)
# from google.cloud import speech


# def speech_to_text(
#     config: speech.RecognitionConfig,
#     audio: speech.RecognitionAudio,
# ) -> speech.RecognizeResponse:
#     client = speech.SpeechClient()
#
#     # Synchronous speech recognition request
#     response = client.recognize(config=config, audio=audio)
#
#     return response
#
#
# def print_response(response: speech.RecognizeResponse):
#     for result in response.results:
#         print_result(result)
#
#
# def print_result(result: speech.SpeechRecognitionResult):
#     best_alternative = result.alternatives[0]
#     print("-" * 80)
#     print(f"language_code: {result.language_code}")
#     print(f"transcript:    {best_alternative.transcript}")
#     print(f"confidence:    {best_alternative.confidence:.0%}")
#
#
