from fastapi import UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import base64
from .url.url_logic import process_url_request

# Manual check model 
class ManualInput(BaseModel):
    claims: str 
    ingredients: str 

# URL request model
class URLRequest(BaseModel):
    url: str

# Default route
async def root():
    return {"message": "Welcome to the VeriTrust Backend API!"}

# Health check route
async def health_check():
    return {"status": "ok"}

# Using Groq's API for OCR
# Read the prompt template
def load_prompt_template():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, 'template', 'check-image-prompt.txt')
    with open(template_path, 'r') as file:
        return file.read()

# Check Image's Content
async def check_image(file: UploadFile = File(...)):
    try:
        from groq import Groq
        
        # Initialize Groq client
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Read the file contents
        contents = await file.read()
        # Convert image to base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        
        # Load the prompt template
        prompt = load_prompt_template()
        
        # Set up instructions and image
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=messages,
            temperature=0, # 0 creativity
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        # Extract content from the response
        result = completion.choices[0].message.content
        return {"extracted-text": result}
        
    except Exception as e:
        return {"extracted-text": f"Error: {str(e)}"}

# URL route
async def check_url(request: URLRequest):
    try:
        result = await process_url_request(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Manual check route

# Load the prompt template
def load_prompt_Manual():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, 'template', 'manual-check-prompt.txt')
    with open(template_path, 'r') as file:
        return file.read()

# Fetch result from the LLM 
def send_to_llm(data:dict) ->str:
    try :
        from groq import Groq 
        #  initialize Groq client

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # prompt for better result 
        prompt = load_prompt_Manual()

        messages= [
            {
                'role':'user',
                'content': [
                    {
                        'type' : 'text' ,
                        'text' :prompt
                    },
                    {
                        'type' : 'text' ,
                        'text' : data['claims']
                    },
                    {
                        'type':'text',
                        'text' : data['ingredients']
                    }
                ]
            }
        ]

        completion =  client.chat.completions.create(
            model= 'llama-3.2-90b-vision-preview',
            messages=messages,
            temperature=0,
            max_completion_tokens=1024,
            top_p=1 ,
            stream=False,
            stop = None
        )

        result  = completion.choices[0].message.content
        return result

    except Exception as e :
        return f"Error : {str(e)}"
    

async def manual_check(manual_data: ManualInput):
    try :
        data = {
            'claims' : manual_data.claims,
            'ingredients' : manual_data.ingredients
        }
        result = send_to_llm(data)
        return {"extracted-text": result}
    except Exception as e:  
        return {"extracted-text": f"Error: {str(e)}"}


# Check Raw 
# This is used to directly generate the response based on just the string
# Works exactly like the manual 
async def check_raw(raw_text: str):
    try:
        from groq import Groq
        
        # Initialize Groq client
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Load the prompt template (using the same as manual check)
        prompt = load_prompt_Manual()
        
        # Set up messages with the raw text
        messages = [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': prompt
                    },
                    {
                        'type': 'text',
                        'text': raw_text
                    }
                ]
            }
        ]
        
        completion = client.chat.completions.create(
            model='llama-3.2-90b-vision-preview',
            messages=messages,
            temperature=0,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None
        )
        
        result = completion.choices[0].message.content
        return {"extracted-text": result}
        
    except Exception as e:
        return {"extracted-text": f"Error: {str(e)}"}
