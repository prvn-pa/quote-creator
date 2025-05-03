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

#def generate_gradient(size):
#    color1 = tuple(random.randint(64, 192) for _ in range(3))
#    color2 = tuple(random.randint(64, 192) for _ in range(3))
#    base = Image.new('RGB', size, color1)
#    top = Image.new('RGB', size, color2)
#    mask = Image.linear_gradient('L').resize(size)
#    return Image.composite(top, base, mask)

def generate_gradient(size):
    palette = sns.color_palette("muted")
    colors = [(int(r*255), int(g*255), int(b*255)) for r, g, b in palette]
    color1, color2 = random.sample(colors, 2)

    base = Image.new('RGB', size, color1)
    top = Image.new('RGB', size, color2)
    mask = Image.linear_gradient('L').resize(size)
    return Image.composite(top, base, mask)

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
    img = generate_gradient(size)
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
        draw.text(((size[0] - w) // 2, current_y), line, font=text_font, fill=(255, 255, 255))
        current_y += h + line_spacing

    current_y += gap_between

    for line in author_lines:
        w = draw.textbbox((0, 0), line, font=name_font)[2]
        h = draw.textbbox((0, 0), line, font=name_font)[3]
        draw.text(((size[0] - w) // 2, current_y), line, font=name_font, fill=(255, 255, 255))
        current_y += h + line_spacing

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

