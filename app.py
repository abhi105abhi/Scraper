import os
import json
import time
import shutil
import threading
import queue
import tempfile
from flask import Flask, render_template, request, send_file, Response
from agent import run_ai_scraper_agent

app = Flask(__name__)

# --- VERCEL FIX: Route all file operations to the ephemeral /tmp directory ---
BASE_DIR = tempfile.gettempdir()
DATA_DIR = os.path.join(BASE_DIR, 'output_data')
ZIP_FILE_PATH = os.path.join(BASE_DIR, "final_dataset.zip")

progress_queue = queue.Queue()

def push_ui_update(step_title, percentage, terminal_log, status="processing"):
    progress_queue.put({
        "step": step_title,
        "percent": percentage,
        "message": f"[{time.strftime('%H:%M:%S')}] {terminal_log}",
        "status": status
    })

def execution_thread_worker(city, api_key):
    try:
        push_ui_update("Cleaning Workspace", 5, "Initializing temporary folder arrays...")
        if os.path.exists(DATA_DIR):
            shutil.rmtree(DATA_DIR)
        if os.path.exists(ZIP_FILE_PATH):
            os.remove(ZIP_FILE_PATH)
        os.makedirs(DATA_DIR, exist_ok=True)

        success = run_ai_scraper_agent(city, api_key, DATA_DIR, push_ui_update)
        
        if success:
            push_ui_update("Packaging Final Dataset", 90, "Compiling multi-relational datasets into standalone zip compression formats...")
            base_name = ZIP_FILE_PATH.replace('.zip', '')
            shutil.make_archive(base_name, 'zip', DATA_DIR)
            push_ui_update("Complete", 100, "[Success] Everything built cleanly! Your download link is ready below.", "completed")
        else:
            pass
            
    except Exception as e:
        push_ui_update("System Exception Encountered", 100, f"[Error] Main operational cluster exception occurred: {str(e)}", "failed")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_pipeline():
    city = request.form.get('city')
    api_key = request.form.get('api_key')
    
    if not city or not api_key:
        return "Missing variables", 400
        
    while not progress_queue.empty():
        try:
            progress_queue.get_nowait()
        except queue.Empty:
            break

    threading.Thread(target=execution_thread_worker, args=(city, api_key)).start()
    return "Pipeline initialized successfully."

@app.route('/progress')
def live_progress_stream():
    def generate_events():
        while True:
            try:
                data = progress_queue.get(timeout=30)
                yield f"data: {json.dumps(data)}\n\n"
                if data['status'] in ['completed', 'failed']:
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'message': '[System] Connection heartbeat active...'})}\n\n"
                
    return Response(generate_events(), mimetype='text/event-stream')

@app.route('/download')
def download_dataset():
    if os.path.exists(ZIP_FILE_PATH):
        return send_file(ZIP_FILE_PATH, as_attachment=True, download_name="scraped_food_data.zip")
    return f"Error: Dataset not found at {ZIP_FILE_PATH}. File generation might have failed silently.", 404

if __name__ == '__main__':
    app.run(debug=False, port=5000)
