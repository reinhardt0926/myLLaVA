from llava.eval.run_llava import eval_model
from llava.mm_utils import get_model_name_from_path


model_path = "liuhaotian/llava-v1.5-7b"
# prompt = "What are the things I should be cautious about when I visit here?"
# image_file = "https://llava-vl.github.io/static/images/view.jpg"
prompt = "Are there more big green things than large purple shiny cubes?"
image_file = "/home/hdseo0388/class/bigdata_computing/PRO-V1/LLaVA/Dataset/CLEVR_v1.0/images/train/CLEVR_train_000000.png"

args = type('Args', (), {
    "model_path": model_path,
    "model_base": None,
    "model_name": get_model_name_from_path(model_path),
    "query": prompt,
    "conv_mode": None,
    "image_file": image_file,
    "sep": ",",
    "temperature": 0,
    "top_p": None,
    "num_beams": 1,
    "max_new_tokens": 512
})()

eval_model(args)