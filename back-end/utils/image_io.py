import base64
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

def open_image(source_path: Path) -> Image.Image:
<<<<<<< HEAD:back-end/utils/image_io.py
    return Image.open(source_path)
=======
    return Image.open(str(source_path)).convert("RGB")
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd:back-end/utils/image_util.py

def open_base64(base64_string: str) -> Image.Image:
    return open_image(BytesIO(base64.b64decode(base64_string)))

def to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format = "PNG")
    return str(base64.b64encode(buffer.getvalue()).decode("utf-8"))

def cut_image(image: Image.Image, bbox: list[int], min_size: int = 50) -> Image.Image:
    image = image.crop(bbox)
    if min(image.height, image.width) < min_size:
        scale = min_size / min(image.size)
        image = image.resize((int(image.width * scale), int(image.height * scale)))
    return image

def draw_annotation(page: Image.Image, elements: list) -> Image.Image:
    drawer = ImageDraw.Draw(page)
    text_font, text_color = ImageFont.load_default(size = 16), "red"

    for order, (x1, y1, x2, y2, conf, type) in enumerate(elements, start = 1):
        text = f"{order}. {type}: {conf:.2f}"
        text_position = (x1, y1 - 20)
        
        drawer.rectangle((x1, y1, x2, y2), outline = text_color, width = 1)
        drawer.text(text_position, text, fill = text_color, font = text_font)
    return page

def save_image(path: Path, image: Image.Image):
    image.save(path)

def save_pdf(path: Path, images: list[Image.Image]):
    if len(images) == 1:
        images[0].save(path)
    else:   
        images[0].save(path, save_all = True, append_images = images[1:])
