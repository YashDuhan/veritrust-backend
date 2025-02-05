from fastapi import UploadFile, File
import os
import base64

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
    template_path = os.path.join(current_dir, 'template', 'check-image-prompt.md')
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
