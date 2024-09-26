"""
Code interpreter
"""

from openai import OpenAI
from e2b_code_interpreter import CodeInterpreter
import base64
import os
import dotenv
import requests
from urllib.parse import urlparse
import io

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
e2b_code_interpreter = CodeInterpreter(api_key=os.getenv('E2B_API_KEY'))

def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def upload_file_for_code_interpreter(file):
    """
    Uploads a file to the code interpreter and returns the path.

    Args:
        file_url (str): URL or file
    """

    if isinstance(file, str):
        if is_url(file):
            # Handle URL case
            response = requests.get(file)
            response.raise_for_status()  # Raises an exception for HTTP errors
            
            filename = os.path.basename(urlparse(file).path) or 'downloaded_file'
            file_object = io.BytesIO(response.content)
            file_object.name = filename
        else:
            raise ValueError("Invalid file URL")
    else:
        # Assume it's already a file object
        file_object = file

    return e2b_code_interpreter.upload_file(file_object)

def handle_png(picture, index):
    """
    Handles the PNG picture and returns the path.
    """

    png_data = base64.b64decode(picture)

    filename = f"chart_{index}.png"

    with open(filename, "wb") as f:
        f.write(png_data)

    print(f"Saved chart to {filename}")
    
    return filename

def code_interpret(code):
    """
    This function executes the code interpreter and returns the results.
    """
    results = []

    print("Running code interpreter...")
    exec = e2b_code_interpreter.notebook.exec_cell(
        code,
        on_stderr=lambda stderr: results.append(stderr),
        on_stdout=lambda stdout: results.append(stdout),
    )

    if exec.error:
        print("[Code Interpreter ERROR]", exec.error)
        return exec.error
    
    for i, result in enumerate(exec.results):
        if result.png:
            filename = handle_png(result.png, i)
            results.append(filename)
        else:
            results.append(result)
    return results



if __name__ == '__main__':  

    SYSTEM_PROMPT = """
    ## your job & context
    you are a python data scientist. you are given tasks to complete and you run python code to solve them.
    - the python code runs in jupyter notebook.
    - every time you call `execute_python` tool, the python code is executed in a separate cell. it's okay to multiple calls to `execute_python`.
    - display visualizations using matplotlib or any other visualization library directly in the notebook. don't worry about saving the visualizations to a file.
    - you have access to the internet and can make api requests.
    - you also have access to the filesystem and can read/write files.
    - you can install any pip package (if it exists) if you need to but the usual packages for data analysis are already preinstalled.
    - you can run any python code you want, everything is running in a secure sandbox environment.
    """

    tools = [
        {
            "type": "function",
            "function": {
            "name": "execute_python",
            "description": "Execute python code in a Jupyter notebook cell and returns any result, stdout, stderr, display_data, and error.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The python code to execute in a single cell."
                    }
                },
                "required": ["code"]
            }
            },
        }
    ]
  
    user_message = "Plot a normal distribution chart"
    file_url = r'https://raw.githubusercontent.com/codeforamerica/ohana-api/refs/heads/master/data/sample-csv/addresses.csv'
    
    print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": [{"type": "text", "text": user_message}]}
    ]

    file_url = upload_file_for_code_interpreter(file_url)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    code_interpreter_results = None

    for choice in response.choices:
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                if tool_call.function.name == "execute_python":
                    print(tool_call)
                    code = eval(tool_call.function.arguments)['code']
                    print("CODE TO RUN:")
                    print(code)
                    code_interpreter_results = code_interpret(code)
        else:
            print("Answer:", choice.message.content)

    if code_interpreter_results:
        print("Code Interpreter Results:")
        print(code_interpreter_results)