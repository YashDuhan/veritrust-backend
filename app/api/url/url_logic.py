"""
FLOW LOGIC:

1. URL Check (process_url_request):
   We check if we actually got a URL to work with. If not, we let the user know 
   they need to provide one. If we have a URL, we pass it along to get its content.

2. Getting the Content (extract_url_content):
   - Use a headless browser (browser without GUI) because:
     a) Many modern websites use JavaScript to load content dynamically
     b) Simple HTTP requests can't execute JavaScript or render dynamic content
     c) Headless browser can fully render the page like a real browser
     d) It's more efficient as we don't need to display anything visually
     e) Works well with Vercel's serverless environment
   - Load the webpage while pretending to be a normal browser (so websites don't block us)
   - Grab the page title and all the text
   - Clean up the content by removing stuff we don't need (images, scripts, ads, etc.)
   - Keep the content under 4000 characters (Groq has limits)
   - Send the cleaned content to our AI for analysis

3. AI Processing (process_with_ai):
   Now we ask our AI to help:
   - Load our custom instructions (from urlPrompt.txt)
   - Send everything to our AI (GROQ's Mixtral model)
   - Keep the AI focused (low temperature setting = more precise answers)[Hallucination means the AI will start thinking it's a human and stop following instructions]
   - Turn that into a JSON object

4. Backup Plan (parseJson.py):
   If the AI's response is messy(not in proper JSON format):
   - We have another AI take a look with stricter instructions
   - If that doesn't work either, we will just return the raw response
"""

from typing import Dict, Optional
import os
from groq import Groq
from playwright.async_api import async_playwright
from .parseJson import parse_with_ai

async def process_url_request(request_data: Dict) -> Dict:
    url = request_data.get('url')
    
    if not url:
        return {
            "status": "error",
            "content": "No URL provided in request"
        }
    
    return await extract_url_content(url)

# using playwright's headless feature
async def extract_url_content(url: str) -> Dict[str, Optional[str]]:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--disable-setuid-sandbox',
                    '--no-sandbox',
                ]
            )
            
            # using custom headers to avoid being blocked by the website like amazon or flipkart 
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            try:
                # waiting for 60 secs to load the page
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_load_state("load", timeout=60000)
                
                # Get title/Claim
                title = await page.title()
                
                # Get all text content from the page
                page_content = await page.evaluate('''() => {
                    // Function to remove unwanted elements
                    function removeElements(selectors) {
                        selectors.forEach(selector => {
                            document.querySelectorAll(selector).forEach(el => el.remove());
                        });
                    }
                    
                    // Remove all non-text elements
                    removeElements([
                        'script',
                        'style',
                        'img',
                        'svg',
                        'video',
                        'audio',
                        'iframe',
                        'canvas',
                        'noscript',
                        'header',
                        'footer',
                        'nav',
                        '.advertisement',
                        '[role="banner"]',
                        '[role="navigation"]',
                        '[role="complementary"]',
                        'button',
                        'select',
                        'input'
                    ]);
                    
                    // Get text content and clean it
                    let text = document.body.innerText;
                    
                    // Remove extra whitespace and normalize
                    text = text.replace(/\\s+/g, ' ').trim();
                    
                    return text;
                }''')
                
                if page_content:
                    # The GROQ's mixtral has a limit of 5000 tokens
                    # Limit content to 4000 characters (keeping 1000 in reserve for prompt and overhead)
                    if len(page_content) > 4000:
                        page_content = page_content[:4000]
                    return await process_with_ai(page_content, title)
                
                return {
                    "status": "error",
                    "content": "No content found on the page."
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "content": f"Error extracting content: {str(e)}"
                }
            finally:
                # Closing the browser and context
                await context.close()
                await browser.close()
                
    except Exception as e:
        return {
            "status": "error",
            "content": f"Error processing content: {str(e)}"
        }

# load prompt
def load_url_prompt():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, 'urlPrompt.txt')
    with open(template_path, 'r') as file:
        return file.read()


async def process_with_ai(content: str, title: str = None) -> Dict:
    # making request to groq
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = load_url_prompt()
        
        # Preparing content for the ai
        full_content = f"""
        Website Title: {title if title else 'Not Found'}
        
        Page Content:
        {content}
        """
        
        messages = [
            {
                "role": "user",
                "content": prompt + "\n" + full_content
            }
        ]
        
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=0.3, # we are using low temp as doesn't need to think too much and to avoid hallucinations
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None
        )
        
        result = completion.choices[0].message.content
        
        # Try to parse the response first
        try:
            parsed_result = eval(result)
            return {
                "status": "success",
                **parsed_result
            }
        except:
            # If failed to parse, try to parse with AI
            ai_parsed = await parse_with_ai(result)
            if ai_parsed["status"] == "success":
                return ai_parsed
            
            # If AI parsing also fails, return raw response
            return {
                "status": "not_parsed",
                "raw_response": result,
                "message": "Could not parse AI response, returning raw output"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "content": f"AI processing error: {str(e)}"
        }


"""
Frontend checks
if the status is:

1. "success":
   - Display the product info normally
   - Show ingredients list
   Example:
   {
       "status": "success",
       "product_info": {
           "title": "Product Name",
           "ingredients": ["ing1", "ing2"],
           "ai_generated": true|false
       }
   }
   - if ai_generated is true, it means the ingredients are generated by the AI and not present in the original product page
   - if ai_generated is false, it means the ingredients are present in the original product page

2. "not_parsed":
   - Show error message
   Example:
   {
       "status": "not_parsed",
       "raw_response": "raw AI text",
       "message": "Could not parse AI response, returning raw output"
   }

3. "error":
   - Show user-friendly error based on content:
     * "No URL provided" -> "Please enter a product URL"
     * "No content found" -> "Couldn't read this page. Try another product URL"
     * "Error extracting content" -> "This page is not accessible right now"
     * "AI processing error" -> "Service is busy, please try again later"
   Example:
   {
       "status": "error",
       "content": "specific error message"
   }
"""