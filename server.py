from flask import Flask, render_template, send_file, jsonify, request
import time
import pyautogui
import threading

class ScreenshotThread(threading.Thread):
    def run(self):
        while True:
            pyautogui.screenshot('screenshot.png')
            time.sleep(1)

thread = ScreenshotThread()
thread.start()  # Start the thread
app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/screenshot')
def screenshot():
    return send_file('screenshot.png', mimetype='image/png')

@app.route('/python', methods=['POST'])
def python_handler():
    # Read JSON data from request body
    print('DEBUG: handling line')
    data = request.get_json()
    
    if 'payload' not in data:
        return jsonify({'answer': 'Error: No payload found'}), 400
    
    text = data['payload']
    
    # Execute the Python code here
    result = exec_python_code(text)
    
    return jsonify({'answer': result})

if __name__ == '__main__':
    app.run(debug=True)

# Example Python code to execute (replace with your own code)
def exec_python_code(text):
    try:
        code = compile(text, 'script', 'exec')
        result = eval(code)
        return str(result)
    except Exception as e:
        return str(e)

