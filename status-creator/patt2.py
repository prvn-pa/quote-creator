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

def catmull_rom_spline(p0, p1, p2, p3, n_points=20):
    """Generates points on a Catmull-Rom spline defined by four control points."""
    points = []
    for i in range(n_points):
        t = i / (n_points - 1)
        t2 = t * t
        t3 = t2 * t

        x = 0.5 * ((2 * p1[0]) +
                   (-p0[0] + p2[0]) * t +
                   (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                   (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)

        y = 0.5 * ((2 * p1[1]) +
                   (-p0[1] + p2[1]) * t +
                   (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                   (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)

        points.append((x, y))
    return points

def generate_wavy_background(width, height, layers=6):
    bg_color = tuple(random.randint(240, 255) for _ in range(3))
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    pastel_colors = [
        (255, 179, 186), (255, 223, 186), (255, 255, 186),
        (186, 255, 201), (186, 225, 255), (221, 201, 255),
        (200, 200, 255), (255, 200, 255), (200, 255, 240)
    ]

    for _ in range(layers):
        amp = random.uniform(height * 0.1, height * 0.25)
        freq = random.uniform(0.002, 0.008)
        phase = random.uniform(0, 2 * math.pi)
        y_offset = random.randint(-height // 4, height + height // 4)
        color = random.choice(pastel_colors)

        # Control points
        step = width // 10
        control_points = []
        for x in range(-step, width + 2 * step, step):
            y = y_offset + amp * math.sin(freq * x + phase) + random.uniform(-10, 10)
            control_points.append((x, y))

        # Add virtual points at start and end for spline continuity
        points = []
        for i in range(1, len(control_points) - 2):
            p0 = control_points[i - 1]
            p1 = control_points[i]
            p2 = control_points[i + 1]
            p3 = control_points[i + 2]
            points.extend(catmull_rom_spline(p0, p1, p2, p3, n_points=20))

        # Complete the shape
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

