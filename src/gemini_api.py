# import os
# import google.generativeai as genai
# from dotenv import load_dotenv


# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel("gemini-2.0-flash")


# def build_prompt(user_question, language, user_level, explain_lines):
    
#     return f'''
# You are an expert coding tutor. A user has asked the following coding question:


# """
# {user_question.strip()}
# """


# Here is how you should respond:
# 1. Summarize the problem clearly.
# 2. Write a full solution in {language}.
# 3. Explain the logic in very simple terms, suitable for a {user_level} level coder.
# 4. {'Also explain every line of code in detail.' if explain_lines else 'You may skip line-by-line explanation.'}


# Avoid complex jargon. Use friendly tone and small steps. Make it engaging and easy to follow.
# '''


# # Streaming Gemini response in real time
# def stream_gemini_response(user_question, language, user_level, explain_lines):
#     prompt = build_prompt(user_question, language, user_level, explain_lines)
#     try:
#         stream = model.generate_content(prompt, stream=True)
#         for chunk in stream:
#             if chunk.text:
#                 yield chunk.text
#     except Exception as e:
#         yield f"❌ Error: {str(e)}"




# import os
# import google.generativeai as genai
# from dotenv import load_dotenv


# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")
# MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
# if not API_KEY:
    
#     raise RuntimeError("GEMINI_API_KEY missing. Create .env from .env.example and set your key.")


# genai.configure(api_key=API_KEY)
# _model = genai.GenerativeModel(MODEL_NAME)

# # ---- Prompt templates ----
# STREAM_PROMPT = """
# You are a friendly coding mentor.
# Respond in Markdown with these sections:
# 1) Problem Summary
# 2) Solution Code ({lang})
# 3) Step-by-step Explanation
# 4) Complexity (time, space)
# 5) At least 2 Sample Test Cases
# {lines}

# Audience level: {level}. Keep it simple and practical. Avoid jargon.
# Problem:


# {question}
# """

# SCRIPT_PROMPT = """
# You are a teaching script writer for an animated video that explains a coding approach.
# Return PLAIN TEXT only (no markdown). Keep sentences short. Output three blocks separated by a single line with three dashes '---':
# BLOCK 1: TITLE (one concise line)
# BLOCK 2: NARRATION (a continuous paragraph the voice will read)
# BLOCK 3: SCENES (bullet-like lines describing visuals per step; max 8 lines). Each line should be 'SCENE: <what to show>'.

# Context:
# - Language: {lang}
# - Level: {level}
# - If a data structure changes over time, mention the key frames (e.g., array indexes, stack push/pop).

# Problem:

# {question}

# """

# # ---- Public helpers ----
# def stream_markdown_answer(question: str, language: str, level: str, explain_lines: bool):
#     prompt = STREAM_PROMPT.format(
#         lang=language,
#         level=level,
#         lines="6) Line-by-line Notes" if explain_lines else "",
#         question=question.strip(),
#     )
#     stream = _model.generate_content(prompt, stream=True)
#     for chunk in stream:
#         text = getattr(chunk, "text", "")
#         if text:
#             yield text


# def get_video_script(question: str, language: str, level: str) -> dict:
#     prompt = SCRIPT_PROMPT.format(
#         lang=language,
#         level=level,
#         question=question.strip()
#     )
#     resp = _model.generate_content(prompt)
#     raw = getattr(resp, "text", "").strip()

#     # Parse three blocks split by '---'
#     title, narration, scenes = "Animated Code Tutor", raw, ""
#     parts = [p.strip() for p in raw.split("---")]
#     if len(parts) >= 3:
#         title, narration, scenes = parts[0], parts[1], parts[2]

#     scene_lines = [
#         s.replace("SCENE:", "").strip()
#         for s in scenes.splitlines()
#         if s.strip()
#     ]

#     return {
#         "title": title or "Animated Code Tutor",
#         "narration": narration,
#         "scenes": scene_lines
#     }





# import os
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")
# MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
# if not API_KEY:
#     raise RuntimeError("GEMINI_API_KEY missing. Create .env from .env.example and set your key.")

# genai.configure(api_key=API_KEY)
# _model = genai.GenerativeModel(MODEL_NAME)

# # ---- Prompt templates ----
# STREAM_PROMPT_HEADER = """
# You are a friendly coding mentor.
# Respond in Markdown with these sections:
# 1) Problem Summary
# 2) Solution Code ({lang})
# 3) Step-by-step Explanation
# 4) Complexity (time, space)
# 5) At least 2 Sample Test Cases
# {lines}

# Audience level: {level}. Keep it simple and practical. Avoid jargon.
# Conversation so far:
# """

# SCRIPT_PROMPT = """
# You are a teaching script writer for an animated video that explains a coding approach.
# Return PLAIN TEXT only (no markdown). Keep sentences short. Output three blocks separated by a single line with three dashes '---':
# BLOCK 1: TITLE (one concise line)
# BLOCK 2: NARRATION (a continuous paragraph the voice will read)
# BLOCK 3: SCENES (bullet-like lines describing visuals per step; max 8 lines). Each line should be 'SCENE: <what to show>'.

# Context:
# - Language: {lang}
# - Level: {level}
# - If a data structure changes over time, mention the key frames (e.g., array indexes, stack push/pop).

# Conversation so far:

# {conversation}
# """

# # ---- Public helpers ----
# def stream_markdown_answer(messages: list, language: str, level: str, explain_lines: bool):
#     """
#     Stream a markdown response based on full conversation history.
#     `messages` is a list of dicts with {"role": "user"/"assistant", "content": "..."}
#     """
#     # Build conversation string
#     conversation_text = ""
#     for msg in messages:
#         if msg["role"] == "user":
#             conversation_text += f"User: {msg['content']}\n"
#         else:
#             conversation_text += f"Assistant: {msg['content']}\n"

#     # Build final prompt
#     prompt = STREAM_PROMPT_HEADER.format(
#         lang=language,
#         level=level,
#         lines="6) Line-by-line Notes" if explain_lines else "",
#     ) + "\n" + conversation_text

#     # Stream from Gemini
#     stream = _model.generate_content(prompt, stream=True)
#     for chunk in stream:
#         text = getattr(chunk, "text", "")
#         if text:
#             yield text


# def get_video_script(messages: list, language: str, level: str) -> dict:
#     # Include chat history in video prompt too
#     conversation_text = ""
#     for msg in messages:
#         conversation_text += f"{msg['role'].capitalize()}: {msg['content']}\n"

#     prompt = SCRIPT_PROMPT.format(
#         lang=language,
#         level=level,
#         conversation=conversation_text.strip()
#     )
#     resp = _model.generate_content(prompt)
#     raw = getattr(resp, "text", "").strip()

#     # Parse three blocks split by '---'
#     title, narration, scenes = "Animated Code Tutor", raw, ""
#     parts = [p.strip() for p in raw.split("---")]
#     if len(parts) >= 3:
#         title, narration, scenes = parts[0], parts[1], parts[2]

#     scene_lines = [
#         s.replace("SCENE:", "").strip()
#         for s in scenes.splitlines()
#         if s.strip()
#     ]

#     return {
#         "title": title or "Animated Code Tutor",
#         "narration": narration,
#         "scenes": scene_lines
#     }




# src/gemini_api.py
# src/gemini_api.py
import google.generativeai as genai
import streamlit as st
from typing import Generator, Dict, Any
import base64
from PIL import Image
import io
from dotenv import load_dotenv
import os

# Configure Gemini API
try:
    
    # from dotenv import load_dotenv
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


    

    genai.configure(api_key=GEMINI_API_KEY)
except:
    st.error("⚠️ Gemini API key not found in secrets!")

def stream_markdown_answer(messages: list, language: str, level: str, explain_lines: bool) -> Generator[str, None, None]:
    """
    Stream markdown answer from Gemini (existing functionality)
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Build context
        context = f"""
        You are CodeExplainer AI, a helpful coding tutor.
        
        User Settings:
        - Programming Language: {language}
        - Skill Level: {level}
        - Line-by-line explanation: {'Yes' if explain_lines else 'No'}
        
        Instructions:
        - Provide clear, educational explanations
        - Use appropriate complexity for {level} level
        - Include practical examples
        - Format code with proper syntax highlighting
        {"- Explain code line by line when requested" if explain_lines else ""}
        """
        
        # Convert messages to Gemini format
        conversation_text = ""
        for msg in messages[:-1]:  # Exclude the empty assistant message
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation_text += f"{role}: {msg['content']}\n\n"
        
        # Get the latest user message
        latest_message = messages[-2]["content"] if len(messages) >= 2 else ""
        
        prompt = f"{context}\n\nConversation History:\n{conversation_text}\n\nLatest Question: {latest_message}\n\nPlease provide a helpful response:"
        
        # Stream response
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        yield f"❌ Error: {str(e)}"

def analyze_image_question(img_base64: str, settings: Dict[str, Any]) -> str:
    """
    Analyze uploaded image containing coding questions
    """
    try:
        # Use Gemini Vision model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Convert base64 to image
        img_data = base64.b64decode(img_base64)
        image = Image.open(io.BytesIO(img_data))
        
        prompt = f"""
        You are CodeExplainer AI, analyzing an uploaded image that contains a coding question or code snippet.
        
        User Settings:
        - Programming Language: {settings['language']}
        - Skill Level: {settings['level']}
        - Line-by-line explanation: {'Yes' if settings['explain_lines'] else 'No'}
        
        Please analyze this image and:
        1. Identify any code, algorithms, or programming concepts shown
        2. Extract the main question or problem being asked
        3. Provide a comprehensive explanation appropriate for {settings['level']} level
        4. If there's code, explain it step by step
        5. Suggest improvements or fixes if needed
        6. Include practical examples
        
        Format your response in markdown with proper code blocks and clear sections.
        """
        
        response = model.generate_content([prompt, image])
        return response.text
        
    except Exception as e:
        return f"❌ Error analyzing image: {str(e)}"

def get_video_script(explanation_text: str, style: str, duration: int) -> Dict[str, Any]:
    """
    Generate video script for animated explanation
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Create a detailed video script for an animated coding explanation video.
        
        Content to explain: {explanation_text}
        Video Style: {style}
        Duration: {duration} minutes
        
        Generate a comprehensive script with:
        1. Scene-by-scene breakdown
        2. Narration text for each scene
        3. Visual elements to show (code, diagrams, animations)
        4. Timing for each scene
        5. Animation descriptions
        6. Key learning points to highlight
        
        Format the response as JSON with this structure:
        {{
            "title": "Video Title",
            "total_duration": {duration},
            "scenes": [
                {{
                    "scene_number": 1,
                    "duration": 30,
                    "narration": "Script text...",
                    "visuals": ["Code block", "Diagram", "Animation"],
                    "animations": ["Fade in", "Highlight", "Step through"],
                    "key_points": ["Point 1", "Point 2"]
                }}
            ],
            "style_notes": "Animation style guidelines"
        }}
        
        Make it engaging and educational for programming concepts.
        """
        
        response = model.generate_content(prompt)
        
        # Try to parse JSON, fallback to structured text
        try:
            import json
            script_data = json.loads(response.text)
            return script_data
        except:
            # Fallback: create structured data from text response
            return {
                "title": f"{style} Explanation",
                "total_duration": duration * 60,
                "content": response.text,
                "style": style
            }
            
    except Exception as e:
        return {
            "title": "Error",
            "content": f"❌ Error generating video script: {str(e)}",
            "style": style
        }

def enhance_explanation_for_video(explanation_text: str, language: str) -> str:
    """
    Enhance explanation specifically for video format
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Take this coding explanation and enhance it specifically for an animated video format:
        
        Original Explanation: {explanation_text}
        Programming Language: {language}
        
        Enhance it by:
        1. Adding visual cues and descriptions
        2. Breaking down complex concepts into visual steps
        3. Including animation suggestions
        4. Making it more narrative and engaging
        5. Adding timing cues for better pacing
        
        Keep the technical accuracy while making it more suitable for video presentation.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return explanation_text  # Return original if enhancement fails

def get_code_visualization_data(code_snippet: str, language: str) -> Dict[str, Any]:
    """
    Generate data for code visualization in videos
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Analyze this {language} code and generate visualization data for an animated explanation video:
        
        Code: {code_snippet}
        
        Generate detailed information about:
        1. Execution flow and step-by-step breakdown
        2. Variable changes throughout execution
        3. Key decision points and branches
        4. Data structure transformations
        5. Visual elements that would help understanding
        6. Common misconceptions to address
        
        Format as JSON:
        {{
            "execution_steps": [
                {{
                    "step": 1,
                    "description": "Step description",
                    "code_line": "specific line",
                    "variables": {{"var1": "value1"}},
                    "visual_note": "What to show visually"
                }}
            ],
            "key_concepts": ["concept1", "concept2"],
            "visualization_suggestions": ["suggestion1", "suggestion2"],
            "common_errors": ["error1", "error2"]
        }}
        """
        
        response = model.generate_content(prompt)
        
        try:
            import json
            return json.loads(response.text)
        except:
            return {"content": response.text}
            
    except Exception as e:
        return {"error": f"Error analyzing code: {str(e)}"}

def generate_interactive_quiz(explanation_text: str, language: str) -> Dict[str, Any]:
    """
    Generate interactive quiz questions based on the explanation
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Based on this coding explanation for {language}, create an interactive quiz:
        
        Explanation: {explanation_text}
        
        Generate 3-5 multiple choice questions that test understanding of:
        1. Core concepts explained
        2. Code functionality
        3. Potential improvements
        4. Common mistakes
        
        Format as JSON:
        {{
            "quiz_title": "Quiz title",
            "questions": [
                {{
                    "question": "Question text",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "correct_answer": "A",
                    "explanation": "Why this is correct"
                }}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        
        try:
            import json
            return json.loads(response.text)
        except:
            return {"error": "Could not generate quiz"}
            
    except Exception as e:
        return {"error": f"Error generating quiz: {str(e)}"}