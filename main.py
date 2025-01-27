
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from typing import List
import openai
import json

# Initialize FastAPI app
app = FastAPI()

# Set your OpenAI API key
openai.api_key = "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"  # Replace with your actual OpenAI API key

# Request model for Practice Mode
class PracticeFeedbackRequest(BaseModel):
    transcription: str  # User's spoken transcription
    mode: str           # "Practice" or "Test"
    part: int           # Part of the test (1, 2, or 3)

# Request model for Test Mode
class TestFeedbackRequest(BaseModel):
    transcriptions: List[str]  # List of transcriptions for all parts (3 parts)
    mode: str                  # "Test"

# Response model
class FeedbackResponse(BaseModel):
    fluency_score: int
    fluency_feedback: str
    grammar_score: int
    grammar_feedback: str
    vocabulary_score: int
    vocabulary_feedback: str
    pronunciation_score: int
    pronunciation_feedback: str

# Endpoint for Practice Mode
@app.post("/feedback", response_model=FeedbackResponse)
async def get_practice_feedback(request: PracticeFeedbackRequest):
    """
    Generate feedback for Practice Mode (single transcription).
    """
    try:
        # Prepare the prompt for OpenAI
        prompt = f"""
You are an IELTS examiner. Provide a detailed evaluation of the transcription below based on IELTS criteria.
Include scores out of 9 for:
- Fluency and Coherence
- Grammar
- Vocabulary
- Pronunciation
Explain the reasons for each score.

Mode: {request.mode}
Part: {request.part}
Transcription: "{request.transcription}"

Return the feedback in the following JSON format:
{{
  "fluency_score": <number>,
  "fluency_feedback": "<string>",
  "grammar_score": <number>,
  "grammar_feedback": "<string>",
  "vocabulary_score": <number>,
  "vocabulary_feedback": "<string>",
  "pronunciation_score": <number>,
  "pronunciation_feedback": "<string>"
}}
        """

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Adjust this to "gpt-4" if needed
            messages=[
                {"role": "system", "content": "You are an IELTS examiner."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract feedback from OpenAI response
        feedback_content = response.choices[0].message.content
        parsed_feedback = json.loads(feedback_content)

        return FeedbackResponse(**parsed_feedback)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating feedback: {e}")

# Endpoint for Test Mode
@app.post("/test_feedback")
async def get_test_feedback(request: TestFeedbackRequest):
    """
    Generate feedback for Test Mode (all parts together).
    """
    try:
        # Validate the number of transcriptions
        if len(request.transcriptions) != 3:
            raise HTTPException(status_code=422, detail="Exactly 3 transcriptions are required for Test Mode.")

        # Prepare the prompt for OpenAI
        prompt = f"""
You are an IELTS examiner. Provide detailed feedback for the following IELTS Speaking Test transcriptions.
Each part of the test should receive scores and feedback for:
- Fluency and Coherence
- Grammar
- Vocabulary
- Pronunciation

Mode: {request.mode}

Part 1 Transcription: "{request.transcriptions[0]}"
Part 2 Transcription: "{request.transcriptions[1]}"
Part 3 Transcription: "{request.transcriptions[2]}"

Return the feedback in this JSON format:
{{
  "part_1_feedback": {{
    "fluency_score": <number>,
    "fluency_feedback": "<string>",
    "grammar_score": <number>,
    "grammar_feedback": "<string>",
    "vocabulary_score": <number>,
    "vocabulary_feedback": "<string>",
    "pronunciation_score": <number>,
    "pronunciation_feedback": "<string>"
  }},
  "part_2_feedback": {{
    ...
  }},
  "part_3_feedback": {{
    ...
  }}
}}
        """

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Adjust this to "gpt-4" if needed
            messages=[
                {"role": "system", "content": "You are an IELTS examiner."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract feedback from OpenAI response
        feedback_content = response.choices[0].message.content
        parsed_feedback = json.loads(feedback_content)

        # Log the feedback for debugging
        print("Generated feedback:", json.dumps(parsed_feedback, indent=2))

        return parsed_feedback

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating feedback: {e}")

# Run the server using uvicorn:
# $ uvicorn main:app --host 0.0.0.0 --port 8000
