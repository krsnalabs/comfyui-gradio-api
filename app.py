import os
import random
import sys

import gradio as gr
from comfy_api_simplified import ComfyApiWrapper, ComfyWorkflowWrapper
import nest_asyncio
nest_asyncio.apply()

# Update these paths based on your ComfyUI setup
INPUT_DIR = os.path.join(os.path.dirname(__file__), "images")
api = ComfyApiWrapper(sys.argv[1])
wf = ComfyWorkflowWrapper("workflow_api.json")

def generate_image(person_image, top_image, bottom_image, top_desc, top_neg_desc, bottom_desc, bottom_neg_desc):
    # Save input images to INPUT_DIR
    person_image_path = os.path.join(INPUT_DIR, "person_image.jpg")
    top_image_path = os.path.join(INPUT_DIR, "top_image.jpg")
    bottom_image_path = os.path.join(INPUT_DIR, "bottom_image.jpg")
    
    # Save uploaded images locally
    person_image.save(person_image_path)
    top_image.save(top_image_path)
    bottom_image.save(bottom_image_path)

    person_image_metadata = api.upload_image(person_image_path)
    top_image_metadata = api.upload_image(top_image_path)
    bottom_image_metadata = api.upload_image(bottom_image_path)

    wf.set_node_param("Load Image (Person)", "image", f"{person_image_metadata['subfolder']}/{person_image_metadata['name']}")
    wf.set_node_param("Load Image (Top)", "image", f"{top_image_metadata['subfolder']}/{top_image_metadata['name']}")
    wf.set_node_param("Load Image (Bottom)", "image", f"{bottom_image_metadata['subfolder']}/{bottom_image_metadata['name']}")

    wf.set_node_param("SDXL Prompt Styler - top", "text_positive", top_desc)
    wf.set_node_param("SDXL Prompt Styler - top", "text_negative", top_neg_desc)
    wf.set_node_param("SDXL Prompt Styler - bottom", "text_positive", bottom_desc)
    wf.set_node_param("SDXL Prompt Styler - bottom", "text_negative", bottom_neg_desc)

    wf.set_node_param("CatVTON Wrapper", "seed", random.randint(1, 1500000))

    results = api.queue_and_wait_images(wf, output_node_title="Save Image")
    for filename, image_data in results.items():
      with open(f"{filename}", "wb+") as f:
          f.write(image_data)
      return filename

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