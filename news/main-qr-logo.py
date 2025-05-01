import requests
import qrcode
import pyshorteners
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = 1000
PADDING = 40
SIDE_MARGIN = 20
IMAGE_BOX_WIDTH = CANVAS_SIZE - 2 * SIDE_MARGIN  # almost full width
IMAGE_BOX_HEIGHT = 420  # double height

TITLE_FONT_SIZE = 55
SUBTITLE_FONT_SIZE = 34
REFERENCE_FONT_SIZE = 20

FONT_BOLD = ImageFont.truetype("fonts/NoticiaText-Bold.ttf", TITLE_FONT_SIZE)
FONT_ITALIC = ImageFont.truetype("fonts/NoticiaText-Regular.ttf", SUBTITLE_FONT_SIZE)
FONT_REF = ImageFont.truetype("fonts/Montserrat-Medium.ttf", REFERENCE_FONT_SIZE)

def generate_qr_code(url, output_path):
    # Shorten the URL
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(url)
    print(f"Shortened URL: {short_url}")

    # Create the QR code instance
    qr = qrcode.QRCode(
        version=1,  # Version 1 generates a 21x21 grid (smallest size)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # Size of each box in the QR code grid
        border=4,  # Border thickness
    )
    qr.add_data(short_url)
    qr.make(fit=True)

    # Create the image from the QR code at a higher resolution (200x200)
    img = qr.make_image(fill='black', back_color='white')

    # Resize the image to 50x50 pixels while maintaining readability
    img = img.resize((100, 100), Image.Resampling.LANCZOS)

    # Save the image as a PNG file
    img.save(output_path, 'PNG')

def draw_wrapped_text(draw, text, font, max_width, y_start, color="black", align="left"):
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        w, _ = draw.textbbox((0, 0), test_line, font=font)[2:]
        if w <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())
    for line in lines:
        w, h = draw.textbbox((0, 0), line, font=font)[2:]
        if align == "left":
            x = PADDING
        else:
            x = CANVAS_SIZE - PADDING - w
        draw.text((x, y_start), line, font=font, fill=color)
        y_start += h
    return y_start
    
def create_image_from_input(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    title = subtitle = image_url = reference = None
    for line in lines:
        if line.startswith("Title:"):
            title = line[len("Title:"):].strip()
        elif line.startswith("Subtitle:"):
            subtitle = line[len("Subtitle:"):].strip()
        elif line.startswith("ImageURL:"):
            image_url = line[len("ImageURL:"):].strip()
        elif line.startswith("Reference:"):
            reference = line[len("Reference:"):].strip()
        elif line.startswith("Link:"):
            link = line[len("Link:"):].strip()

    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), "white")
    draw = ImageDraw.Draw(img)

    y = PADDING
    y = draw_wrapped_text(draw, title, FONT_BOLD, CANVAS_SIZE - 2 * PADDING, y, align="left")
    y += 40
    y = draw_wrapped_text(draw, subtitle, FONT_ITALIC, CANVAS_SIZE - 2 * PADDING, y, color="black", align="left")
    y += 40

    try:
        response = requests.get(image_url)
        linked_img = Image.open(BytesIO(response.content)).convert("RGB")
    except Exception as e:
        raise ValueError(f"Failed to download or open image: {e}")

    # Scale and crop the linked image to exactly IMAGE_BOX_WIDTH x IMAGE_BOX_HEIGHT
    img_ratio = linked_img.width / linked_img.height
    target_ratio = IMAGE_BOX_WIDTH / IMAGE_BOX_HEIGHT

    if img_ratio > target_ratio:
        # Image is wider: fit height
        scale_factor = IMAGE_BOX_HEIGHT / linked_img.height
    else:
        # Image is taller or equal: fit width
        scale_factor = IMAGE_BOX_WIDTH / linked_img.width

    new_width = int(linked_img.width * scale_factor)
    new_height = int(linked_img.height * scale_factor)

    resized_img = linked_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Center crop to exact size
    left = (new_width - IMAGE_BOX_WIDTH) // 2
    top = (new_height - IMAGE_BOX_HEIGHT) // 2
    right = left + IMAGE_BOX_WIDTH
    bottom = top + IMAGE_BOX_HEIGHT

    cropped_img = resized_img.crop((left, top, right, bottom))

    # Compute paste position
    paste_x = SIDE_MARGIN  # always 20px
    paste_y = y

    img.paste(cropped_img, (paste_x, paste_y))
    
    ref_y = paste_y + IMAGE_BOX_HEIGHT + 15

    # Generate and paste QR code image
    generate_qr_code(link, 'qrcode.png')    
    qrcode = Image.open("qrcode.png")
    img.paste(qrcode, (SIDE_MARGIN, ref_y))

    # Download and resize logo to 100x100
    try:
        logo_response = requests.get(reference, timeout=10)
        logo_response.raise_for_status()

        content_type = logo_response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            raise ValueError(f"URL does not point to an image. Content-Type: {content_type}")

        logo_img = Image.open(BytesIO(logo_response.content)).convert("RGBA")

        # Resize proportionally: height = 100 px, width scaled accordingly
        desired_height = 40
        aspect_ratio = logo_img.width / logo_img.height
        new_width = int(desired_height * aspect_ratio)
        logo_img = logo_img.resize((new_width, desired_height), Image.Resampling.LANCZOS)

    except Exception as e:
        raise ValueError(f"Failed to download or open logo: {e}")

    # Paste logo to the right side of QR code
    logo_x = CANVAS_SIZE - SIDE_MARGIN - logo_img.width
    img.paste(logo_img, (logo_x, ref_y), mask=logo_img if logo_img.mode == "RGBA" else None)

    output_path = "output_image.jpg"
    img.save(output_path)

create_image_from_input("input.txt")

