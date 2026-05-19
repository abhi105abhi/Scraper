import os
import re
import traceback
from google import genai

def clean_generated_code(text):
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def run_ai_scraper_agent(city, api_key, output_dir, update_progress):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        update_progress("Authentication Failure.", 0, f"[Error] API Key configuration failed: {str(e)}", "failed")
        return False

    update_progress("Analyzing Target Targets", 10, "[System] Linked to Gemini AI. Building targeted target logic prompts...")

    # Escape backslashes for Windows so the AI doesn't break the path
    safe_output_dir = output_dir.replace('\\', '/')
    
    base_prompt = f'''
    Write a complete Python script to mock or fetch data for Zomato and Swiggy for the city: '{city}'.
    The script must generate exactly 3 distinct CSV files inside the folder path '{safe_output_dir}':
    1. `restaurants.csv` (Columns: name, cuisine, rating, address) - Target top 50 restaurants.
    2. `menus.csv` (Columns: restaurant_name, item_name, price, category)
    3. `reviews.csv` (Columns: restaurant_name, reviewer_name, rating, review_text)
    
    Ensure robust structures. Use standard internal libraries (`requests`, `csv`, `json`, `os`, `random`) so the execution environment requires no third-party installations. If target platform blocks arise due to defensive CDNs, dynamically map out mock real-world dataset layers to fit the 3 dataset target shapes exactly.
    Return ONLY executable, pure Python code block enclosed in ```python ``` tags. No introductory sentences.
    '''
    
    max_retries = 3
    current_prompt = base_prompt
    
    for attempt in range(max_retries):
        try:
            step_num = attempt + 1
            percent_offset = 20 + (attempt * 20)
            
            update_progress(
                f"Generating Automation Code (Attempt {step_num})", 
                percent_offset, 
                f"[Agent] Prompting Gemini to architect parsing scripts..."
            )
            
            response = model.generate_content(current_prompt)
            code = clean_generated_code(response.text)
            
            update_progress(
                f"Executing Generated Script (Attempt {step_num})", 
                percent_offset + 10, 
                f"[Agent] Validating code blocks locally using exec()..."
            )
            
            exec_context = {}
            exec(code, exec_context)
            
            update_progress("Validating Datasets Structure", 80, "[Success] Execution completed. Parsing dataset directory files...")
            
            required_files = ['restaurants.csv', 'menus.csv', 'reviews.csv']
            missing = [f for f in required_files if not os.path.exists(os.path.join(output_dir, f))]
            
            if missing:
                raise FileNotFoundError(f"Generated code executed but failed to build output files: {', '.join(missing)}")
                
            return True
            
        except Exception as e:
            error_msg = traceback.format_exc()
            update_progress(
                f"Self-Healing Activation Loops", 
                25 + (attempt * 25), 
                f"[Error] Runtime execution crashed:\n{str(e)}"
            )
            
            current_prompt = f'''
            The previously generated code threw a runtime compilation error.
            
            --- CRASH DETAILS ---
            {error_msg}
            --- END DETAILS ---
            
            Analyze the script errors and rewrite the script perfectly to fix this issue.
            Ensure it saves `restaurants.csv`, `menus.csv`, and `reviews.csv` in '{safe_output_dir}'.
            Return ONLY raw executable code enclosed within standard ```python ``` markdown wrappers.
            '''
            
    update_progress("Pipeline Aborted", 100, "[Error] Critical agent limits hit. Self-healing retries exhausted.", "failed")
    return False
