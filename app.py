import json
import os
import time
import random
import sys

import gradio as gr
import numpy as np
import requests
from PIL import Image

# Update these paths based on your ComfyUI setup
INPUT_DIR = os.path.join(os.path.dirname(__file__), "images")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

cached_seed = 0

def get_latest_image(folder):
    files = os.listdir(folder)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
    latest_image = os.path.join(folder, image_files[-1]) if image_files else None
    return latest_image

def start_queue(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    requests.post(sys.argv[1], data=data)

def prepare_prompt(person_image_path, top_image_path, bottom_image_path, top_desc, top_neg_desc, bottom_desc, bottom_neg_desc):
    # Load the workflow from your workflow JSON
    with open("workflow_api.json", "r") as file_json:
        prompt = json.load(file_json)

    # Set paths for person, top, and bottom images
    prompt["10"]["inputs"]["image"] = person_image_path
    prompt["11"]["inputs"]["image"] = top_image_path
    prompt["16"]["inputs"]["image"] = bottom_image_path

    # Customize descriptions
    prompt["22"]["inputs"]["text_positive"] = top_desc
    prompt["22"]["inputs"]["text_negative"] = top_neg_desc
    prompt["24"]["inputs"]["text_positive"] = bottom_desc
    prompt["24"]["inputs"]["text_negative"] = bottom_neg_desc

    # Randomize seed for variation
    prompt["14"]["inputs"]["seed"] = random.randint(1, 1500000)
    return prompt

def generate_image(person_image, top_image, bottom_image, top_desc, top_neg_desc, bottom_desc, bottom_neg_desc):
    # Save input images to INPUT_DIR
    person_image_path = os.path.join(INPUT_DIR, "person_image.jpg")
    top_image_path = os.path.join(INPUT_DIR, "top_image.jpg")
    bottom_image_path = os.path.join(INPUT_DIR, "bottom_image.jpg")

    # Save uploaded images locally
    person_image.save(person_image_path)
    top_image.save(top_image_path)
    bottom_image.save(bottom_image_path)

    # Prepare prompt
    prompt = prepare_prompt(
        person_image_path,
        top_image_path,
        bottom_image_path,
        top_desc,
        top_neg_desc,
        bottom_desc,
        bottom_neg_desc
    )

    # Check cached seed to avoid duplicate requests
    global cached_seed
    if cached_seed == prompt["14"]["inputs"]["seed"]:
        return get_latest_image(OUTPUT_DIR)
    cached_seed = prompt["14"]["inputs"]["seed"]

    # Trigger image generation via API
    previous_image = get_latest_image(OUTPUT_DIR)
    start_queue(prompt)

    # Wait for the output to be generated
    while True:
        latest_image = get_latest_image(OUTPUT_DIR)
        if latest_image != previous_image:
            return latest_image

        time.sleep(1)

# Set up Gradio Interface
demo = gr.Interface(
    fn=generate_image,
    inputs=[
        gr.Image(type="pil", label="Person Image"),
        gr.Image(type="pil", label="Top Image"),
        gr.Image(type="pil", label="Bottom Image"),
        gr.Textbox(lines=1, placeholder="Positive description for top", label="Top Positive Description"),
        gr.Textbox(lines=1, placeholder="Negative description for top", label="Top Negative Description"),
        gr.Textbox(lines=1, placeholder="Positive description for bottom", label="Bottom Positive Description"),
        gr.Textbox(lines=1, placeholder="Negative description for bottom", label="Bottom Negative Description")
    ],
    outputs=gr.Image(type="pil", label="Generated Image"),
    title="Fashion AI Image Generation",
    description="Upload person, top, and bottom images, and set positive/negative descriptions."
)

# Launch Gradio App
demo.launch(share=True)