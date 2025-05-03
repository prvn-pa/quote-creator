from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import time
import os
import math

# Font definitions
TEXT_FONTS = {
    'en': ['Inter.ttf', 'Inter.ttf'],
    'ta': ['Notoserif.ttf', 'Notoserif.ttf']
}
NAME_FONTS = {
    'en': ['Inria.ttf', 'Inria.ttf'],
    'ta': ['Tiro.ttf', 'Tiro.ttf']
}

def generate_wavy_background(width, height, layers=5):
    bg_color = tuple(random.randint(240, 255) for _ in range(3))
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    pastel_colors = [
        (255, 179, 186), (255, 223, 186), (255, 255, 186),
        (186, 255, 201), (186, 225, 255), (221, 201, 255),
        (200, 200, 255), (255, 200, 255), (200, 255, 240)
    ]

    base_y = height // 2
    for i in range(layers):
        amp = random.uniform(20, 80)
        freq = random.uniform(0.005, 0.02)
        phase = random.uniform(0, 2 * math.pi)
        y_offset = base_y + (i - layers // 2) * 60 + random.randint(-30, 30)
        color = random.choice(pastel_colors)
        points = [(x, y_offset + amp * math.sin(freq * x + phase)) for x in range(0, width + 10, 5)]
        points += [(width, height), (0, height)]
        draw.polygon(points, fill=color)

    return image

def detect_language(text):
    for c in text:
        if '\u0B80' <= c <= '\u0BFF':
            return 'ta'
    return 'en'

def parse_input(text):
    parts = text.strip().split('\n\n')
    body = parts[0]#.replace('\n', ' ')
    author = parts[1] if len(parts) > 1 else ''
    return body, author

def wrap_text(draw, text, font, max_width):
    lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split()
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
        if not words:  # Preserve empty lines
            lines.append("")
    return lines

def create_image(size, body, author, lang, outname):
    img = generate_wavy_background(*size)
    draw = ImageDraw.Draw(img)

    text_font = ImageFont.truetype(random.choice(TEXT_FONTS[lang]), size[0] // 15)
    name_font = ImageFont.truetype(random.choice(NAME_FONTS[lang]), size[0] // 22)

    max_text_width = size[0] * 0.8

    if size[0] == size[1]:  # Square image
        text_font = ImageFont.truetype(random.choice(TEXT_FONTS[lang]), size[0] // 25)
        name_font = ImageFont.truetype(random.choice(NAME_FONTS[lang]), size[0] // 30)
        max_text_width = size[0] * 0.75

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
        draw.text(((size[0] - w) // 2, current_y), line, font=text_font, fill=(50, 50, 50))
        current_y += h + line_spacing

    current_y += gap_between

    for line in author_lines:
        w = draw.textbbox((0, 0), line, font=name_font)[2]
        h = draw.textbbox((0, 0), line, font=name_font)[3]
        draw.text(((size[0] - w) // 2, current_y), line, font=name_font, fill=(50, 50, 50))
        current_y += h + line_spacing

    img.save(outname, 'JPEG', quality=95)

# Main Execution
with open('input.txt', 'r', encoding='utf-8') as f:
    content = f.read()

body, author = parse_input(content)
lang = detect_language(body)

timestamp = int(time.time())
os.makedirs('output', exist_ok=True)

create_image((1080, 1920), body, author, lang, f'output/wa_{timestamp}.jpg')
create_image((1080, 1080), body, author, lang, f'output/sq_{timestamp}.jpg')

print("Images generated successfully!")

