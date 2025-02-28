from fastapi import UploadFile, File, HTTPException
from pydantic import BaseModel, Field, validator
import os
import base64
from .url.url_logic import process_url_request
import json

# Manual check model 
class ManualInput(BaseModel):
    claims: str 
    ingredients: str 

# Suggestion model
class SuggestionInput(BaseModel):   
    claims: str
    ingredients: str

# Health check model
class HealthCheckInput(BaseModel):
    age: int = Field(..., description="Age in years")
    height: float = Field(..., description="Height in centimeters")
    weight: float = Field(..., description="Weight in kilograms")
    gender: str = Field(..., description="Gender identity")
    activity_level: str = Field(..., description="Activity level")
    medical_conditions: str = Field("", description="Any existing medical conditions")
    medications: str = Field("", description="Current medications")
    diet: str = Field("", description="Description of typical diet")
    sleep: float = Field(..., description="Average hours of sleep per day")
    stress: int = Field(..., description="Stress level on a scale of 1-10")
    exercise: str = Field("", description="Description of exercise routine")

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



# Suggestion route logic starts from here 
    
def load_prompt_suggestion():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, 'template', 'suggestion-prompt.txt')
    with open(template_path, 'r') as file:
        return file.read()

def suggestion_from_llm(data:dict) ->object:
    try :
        from groq import Groq 
        #  initialize Groq client

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # prompt for better result 
        prompt = load_prompt_suggestion()

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
                        'text' : f"Claims: {data['claims']}"
                    },
                    {
                        'type':'text',
                        'text' : f"Ingredients: {data['ingredients']}"
                    }
                ]
            }
        ]

        completion =  client.chat.completions.create(
            model= 'llama-3.3-70b-versatile',
            messages=messages,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1 ,
            stream=False,
            response_format={'type':"json_object"},
            stop = None
        )

        result  = completion.choices[0].message.content
        return result

    except Exception as e :
        return f"Error : {str(e)}"


# suggestion route
async def suggestions(manual_data: SuggestionInput):
    try :
        data = {
            'ingredients' : manual_data.ingredients,
            'claims': manual_data.claims
        }
        result = suggestion_from_llm(data)
        return {"response": result}
    except Exception as e:  
        return {"response": f"Error: {str(e)}"}

# Check User's health
async def check_health(health_data: HealthCheckInput):
    try:
        from groq import Groq
        
        # Initialize Groq client
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Load the prompt template
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, 'template', 'check-health-prompt.txt')
        with open(template_path, 'r') as file:
            prompt = file.read()
        
        # Format the health data
        health_info = (
            f"Age: {health_data.age}\n"
            f"Height: {health_data.height} cm\n"
            f"Weight: {health_data.weight} kg\n"
            f"Gender: {health_data.gender}\n"
            f"Activity Level: {health_data.activity_level}\n"
            f"Medical Conditions: {health_data.medical_conditions}\n"
            f"Current Medications: {health_data.medications}\n"
            f"Diet Description: {health_data.diet}\n"
            f"Sleep Hours: {health_data.sleep}\n"
            f"Stress Level (1-10): {health_data.stress}\n"
            f"Exercise Routine: {health_data.exercise}\n"
        )
        
        # Set up messages
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
                        'text': health_info
                    }
                ]
            }
        ]
        
        # Call the AI model
        completion = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=messages,
            temperature=0.2,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            response_format={'type': 'json_object'},
            stop=None
        )
        
        # Parse the result
        result = completion.choices[0].message.content
        parsed_result = json.loads(result)
        
        # Return the parsed JSON directly
        return parsed_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
