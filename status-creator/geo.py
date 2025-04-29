from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import time
import os
import seaborn as sns

# Font definitions
TEXT_FONTS = {
    'en': ['Inter.ttf', 'Inter.ttf'],
    'ta': ['Notoserif.ttf', 'Notoserif.ttf']
}
NAME_FONTS = {
    'en': ['Inria.ttf', 'Inria.ttf'],
    'ta': ['Tiro.ttf', 'Tiro.ttf']
}

# Soft pastel palette (RGB)
PASTEL_COLORS = [
    (255, 179, 186), (255, 223, 186), (255, 255, 186),
    (186, 255, 201), (186, 225, 255), (221, 201, 255),
    (200, 200, 255), (255, 200, 255), (200, 255, 240)
]

SHAPES = ['circle', 'square', 'triangle']

def get_translucent_color():
    base = random.choice(PASTEL_COLORS)
    alpha = random.randint(100, 180)  # Transparent
    return base + (alpha,)

def draw_shape(draw: ImageDraw.Draw, shape: str, x: int, y: int, size: int, color: tuple):
    if shape == 'circle':
        draw.ellipse([x, y, x + size, y + size], fill=color)
    elif shape == 'square':
        draw.rectangle([x, y, x + size, y + size], fill=color)
    elif shape == 'triangle':
        center = (x + size // 2, y + size // 2)
        points = [
            (x + size // 2, y),
            (x, y + size),
            (x + size, y + size)
        ]
        angle = random.uniform(0, 360)
        rotated = rotate_points(points, angle, center)
        draw.polygon(rotated, fill=color)

def rotate_points(points, angle_deg, center):
    import math
    angle_rad = math.radians(angle_deg)
    cx, cy = center
    rotated = []
    for x, y in points:
        dx, dy = x - cx, y - cy
        rx = cx + dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        ry = cy + dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        rotated.append((rx, ry))
    return rotated

def generate_geometric_art(width, height, max_shapes=5):
    bg_color = tuple(random.randint(240, 255) for _ in range(3)) + (255,)
    image = Image.new('RGBA', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image, 'RGBA')

    for _ in range(random.randint(3, max_shapes)):
        shape = random.choice(SHAPES)
        color = get_translucent_color()
        
        # Increase the size by 3 times
        size = random.randint(width // 3, int(width / 1.5)) * 3  # Increased size

        x = random.randint(-size // 4, width - size // 2)
        y = random.randint(-size // 4, height - size // 2)
        draw_shape(draw, shape, x, y, size, color)

    return image


def detect_language(text):
    for c in text:
        if '\u0B80' <= c <= '\u0BFF':
            return 'ta'
    return 'en'

def parse_input(text):
    parts = text.strip().split('\n\n')
    body = parts[0].replace('\n', ' ')
    author = parts[1] if len(parts) > 1 else ''
    return body, author

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if font.getlength(test_line) <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def create_image(size, body, author, lang, outname):
    img = generate_geometric_art(size[0], size[1])  # Corrected this line
    draw = ImageDraw.Draw(img)

    text_font = ImageFont.truetype(random.choice(TEXT_FONTS[lang]), size[0] // 15)
    name_font = ImageFont.truetype(random.choice(NAME_FONTS[lang]), size[0] // 22)

    max_text_width = size[0] * 0.8

    # Adjust font size dynamically for square images
    if size[0] == size[1]:  # Square image (for Twitter post)
        text_font = ImageFont.truetype(random.choice(TEXT_FONTS[lang]), size[0] // 25)
        name_font = ImageFont.truetype(random.choice(NAME_FONTS[lang]), size[0] // 30)
        max_text_width = size[0] * 0.75  # Adjust width for square aspect ratio

    body_lines = wrap_text(draw, body, text_font, max_text_width)
    author_lines = wrap_text(draw, author, name_font, max_text_width)

    line_spacing = size[1] // 80
    gap_between = size[1] // 25

    def text_height(lines, font):
        return sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines) + line_spacing * (len(lines) - 1)

    body_height = text_height(body_lines, text_font)
    author_height = text_height(author_lines, name_font)

    total_height = body_height + gap_between + author_height
    current_y = (size[1] - total_height) // 2

    for line in body_lines:
        w = draw.textbbox((0, 0), line, font=text_font)[2]
        h = draw.textbbox((0, 0), line, font=text_font)[3]
        draw.text(((size[0] - w) // 2, current_y), line, font=text_font, fill=(50, 50, 50))  # Dark gray text
        current_y += h + line_spacing

    current_y += gap_between

    for line in author_lines:
        w = draw.textbbox((0, 0), line, font=name_font)[2]
        h = draw.textbbox((0, 0), line, font=name_font)[3]
        draw.text(((size[0] - w) // 2, current_y), line, font=name_font, fill=(50, 50, 50))  # Dark gray text
        current_y += h + line_spacing

    # Convert to RGB before saving as JPEG to remove transparency
    img = img.convert('RGB')
    
    img.save(outname, 'JPEG', quality=95)



# Main Execution
with open('input.txt', 'r', encoding='utf-8') as f:
    content = f.read()

body, author = parse_input(content)
lang = detect_language(body)

timestamp = int(time.time())
os.makedirs('output', exist_ok=True)

create_image((1080, 1920), body, author, lang, f'output/wa_{timestamp}.jpg')  # WhatsApp Status
create_image((1080, 1080), body, author, lang, f'output/sq_{timestamp}.jpg')  # Twitter Square

print("Images generated successfully!")

