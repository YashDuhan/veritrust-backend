# This file is used to parse the json response from the raw response of the ai, just in case the ai hallucinates

from typing import Dict
import os
from groq import Groq

def load_parse_prompt():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir,'parsePrompt.txt')
    with open(template_path, 'r') as file:
        return file.read()

async def parse_with_ai(raw_response: str) -> Dict:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = load_parse_prompt()
        
        messages = [
            {
                "role": "user",
                "content": prompt + "\n" + raw_response
            }
        ]
        
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=0.1,  # Very low temperature for consistent parsing
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None
        )
        
        result = completion.choices[0].message.content
        
        # Try to parse the AI's response
        try:
            parsed_result = eval(result)
            return {
                "status": "success",
                **parsed_result
            }
        except:
            return {
                "status": "error",
                "content": "Failed to parse JSON even after AI processing"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "content": f"Error in AI parsing: {str(e)}"
        }

