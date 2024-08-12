import torch
from transformers import pipeline
import gradio as gr
from openpyxl import load_workbook
from datetime import datetime
import threading

# Demo for the Active Life Lab's VO2MAX test results analyser
# The language model requires a GPU with at least 16GB of memory, tested on NVIDIA A100 80GB
# Interface created using Gradio and launched listening to incoming connections in port 7860

class ModelManager:
    # Model manager class to handle loading and unloading of the model
    def __init__(self, idle_time=300):  # idle_time in seconds
        self.model = None
        self.idle_time = idle_time
        self.timer = None
        self.lock = threading.Lock()

    def load_model(self):
        """Load the model into memory."""
        if self.model is None:
            print("Loading model...")
            self.model = pipeline(model='openchat/openchat-3.5-1210', do_sample=True, return_full_text=False, torch_dtype=torch.bfloat16, device_map="cuda")
        return self.model

    def reset_timer(self):
        """Reset the timer whenever the model is accessed."""
        with self.lock:
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(self.idle_time, self.unload_model)
            self.timer.start()

    def unload_model(self):
        """Unload the model by deleting it."""
        with self.lock:
            if self.model is not None:
                print("Unloading model due to inactivity.")
                del self.model
                torch.cuda.empty_cache()
                self.model = None

    def get_model(self):
        """Access point for external calls, ensures model is loaded and timer is reset."""
        self.reset_timer()
        return self.load_model()

def inferencer(input_text, temperature):
    if input_text is None:
        return "Please upload a file"
    elif input_text == "Please upload a file":
        return "Please upload a file"
    elif input_text == "":
        return "Please upload a file"
    pipe = manager.get_model()
        
    output = pipe(input_text, max_length=500, temperature=temperature, top_p=0.85, repetition_penalty=1.2)[0]['generated_text']
    output = extract_answer(output)
    if output == "":
        output = pipe(input_text, max_length=500, temperature=temperature, top_p=0.85, repetition_penalty=1.2)[0]['generated_text']
        output = extract_answer(output)
    output = remove_everything_after_empty_line(output)

    return output

def extract_answer(input_text):
    parts = input_text.split("Answer: ")
    if len(parts) > 1:
        return parts[1]
    else:
        return input_text

def remove_input_from_output(input_text, output_text):
    if output_text.startswith(input_text):
        return output_text[len(input_text):].strip()

def remove_starting_text(input_text):
    if input_text.startswith("Answer: "):
        return input_text[len("Answer: "):].strip()

def remove_everything_after_empty_line(input_text):
    return input_text.split('\n\n', 1)[0]

def strip_whitespaces_from_start(input_text):
    number_of_whitespaces_from_start = 0
    for i in range(len(input_text)):
        if input_text[i] != ' ':
            break
        number_of_whitespaces_from_start += 1
    
    if number_of_whitespaces_from_start != 0:
        return input_text[number_of_whitespaces_from_start].strip()
    else:
        return 
    
def calculate_age(date_of_birth):
    # Function to calculate test subject's age. Date of birth is reported in DD/MM/YYYY format
    dob = datetime.strptime(date_of_birth, '%d/%m/%Y')
    current_date = datetime.now()
    age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))
    return age

def create_prompt(file):
    if file is None:
        return "Please upload a file"
    
    # Load the Excel file
    workbook = load_workbook(file)
 
    # Specify the sheet name
    sheet = workbook['MetasoftStudio']  
 
    # Pre-test information
    date_of_birth = sheet['C30'].value
    age = calculate_age(date_of_birth)
    gender = sheet['C29'].value  
    height = sheet['C34'].value  
    weight = sheet['C35'].value  
    bmi = sheet['C40'].value  
 
    # Test results
    duration = sheet['C96'].value
    vo2_normal_measured = sheet['N108'].value  
    vo2_max_measured = sheet['O108'].value  
    heartrate_normal = sheet['N113'].value
    heartrate_max = sheet['O113'].value
    vo2_normal = sheet['N110'].value  
    vo2_max = sheet['O110'].value
 
    #Prompts for language model
    prompt_setup = "You are a personal trainer who is analyzing the results of a VO2MAX test for a client. The client is"
    prompt_physical_info = f"{age} years old {gender}, height is {height}, weight is {weight} and BMI is {bmi}."
    prompt_test_results = f"The clients test results were: normal VO2 value was {vo2_normal} ml/min/kg ({vo2_normal_measured} L/min measured) and absolute maximum {vo2_max} ml/min/kg ({vo2_max_measured} L/min measured). Normal heartrate was {heartrate_normal} bpm and absolute maximum heartrate was {heartrate_max} bpm."
    prompt_question = 'What is the interpretation of clients VO2MAX test results? Should the client be concerned the results? Explain the results assuming that the client has no knowledge about sports medicine and sports science. Start your response with "Answer: " and answer to the client directly.'

    final_prompt = prompt_setup + " " + prompt_physical_info + " " + prompt_test_results + " " + prompt_question

    return final_prompt
    
def check_if_input_text_is_empty(input_text):
    if input_text == "":
        return "Please upload a file"
    if input_text is "Please upload a file":
        return "Please upload a file"

manager = ModelManager(idle_time=300)

#file_info = "File should be in Excel format"
temperature_info = "Higher temperature means more creative responses, but can be less coherent."
info_label = "## VO2MAX test results analyser with OpenChat language model"
info_text = "This app uses OpenChat model to generate responses to the prompt. The prompt is generated based on the information in the uploaded Excel file."
info_text_2 = "The simplification of the report generated by the device used for testing maximal oxygen uptake by the Active Life Lab's treadmill produces a report that is difficult to interpret. The goal of the pilot is to provide a clearer interpretation of the report through the use of artificial intelligence, so that the user can benefit more from it."
with gr.Blocks(title="VO2MAX test results analyser with OpenChat language model") as demo:
    gr.Markdown(info_label)
    gr.Markdown(info_text)
    gr.Markdown(info_text_2)


    with gr.Row(equal_height=False):
        input_text = gr.Textbox(label="Prompt to OpenChat model")
        output_text = gr.Textbox(label="OpenChat model response")

    with gr.Row(equal_height=False):
        
        file = gr.File(label="Upload a Excel file", file_types=['.xlsx'])
        with gr.Group():
            temperature = gr.Slider(minimum=0.1, maximum=1.0, value=0.6, label="Temperature", info=temperature_info, step=0.1)
            submit = gr.Button("Analyze test results in OpenChat model")
    
    file.change(fn=create_prompt, inputs=file, outputs=input_text)
    input_text.change(fn=check_if_input_text_is_empty, inputs=input_text, outputs=output_text)
    
    submit.click(inferencer, inputs=[input_text, temperature], outputs=[output_text])

demo.launch(server_name="0.0.0.0", server_port=7860, root_path="/AIKO/activelifelab-demo")
