import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import textwrap

# Paths to fonts on your system
#TITLE_FONT = "TiltWarp-Regular.ttf"
#TEXT_FONT = "Poppins-Regular.ttf"
#Fonts for Tamil posters
TITLE_FONT = "TiroTamil-Regular.ttf"
TEXT_FONT = "NotoSansTamil-Regular.ttf"

def read_book_data():
    try:
        with open("input.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
            if len(lines) < 6:
                raise ValueError("File must have at least 6 lines.")
            return {
                "image_url": lines[0],
                "title": lines[1],
                "author": lines[2],
                "genre": lines[3],
                "year": lines[4],
                "rating": float(lines[5])
            }
    except Exception as e:
        print(f"Error reading book data: {e}")
        return None
        
def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except Exception:
        pass
    return None

def get_star_icons(rating, assets_path="assets"):
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    icons = ["star_full.png"] * full_stars + ["star_half.png"] * half_star + ["star_empty.png"] * empty_stars
    return [Image.open(os.path.join(assets_path, icon)).convert("RGBA") for icon in icons]

def draw_rating(poster_img, rating, assets_path="assets", spacing=10, y_offset=30, label_font_path=TEXT_FONT):
    stars = get_star_icons(rating, assets_path)
    if not stars:
        return

    draw = ImageDraw.Draw(poster_img)
    label_font = ImageFont.truetype(label_font_path, 16)

    star_width, star_height = stars[0].size
    total_star_width = len(stars) * star_width + (len(stars) - 1) * spacing

    label_text = "My Rating:"
    label_bbox = label_font.getbbox(label_text)
    label_width = label_bbox[2] - label_bbox[0]
    label_height = label_bbox[3] - label_bbox[1]
    label_x = (poster_img.width - label_width) // 2
    label_y = poster_img.height - star_height - y_offset - label_height - 10

    draw.text((label_x, label_y), label_text, font=label_font, fill="black")

    x_start = (poster_img.width - total_star_width) // 2
    y_start = label_y + label_height + 15

    for i, star in enumerate(stars):
        x = x_start + i * (star_width + spacing)
        poster_img.paste(star, (x, y_start), star)

def generate_book_poster(book_info, cover_img):
    poster_width, poster_height = 640, 960
    poster = Image.new("RGB", (poster_width, poster_height), color="#e4e0d8")

    # Step 1: Resize cover image to width = 400 while maintaining aspect ratio
    desired_width = 380
    orig_w, orig_h = cover_img.size
    aspect_ratio = orig_h / orig_w
    desired_height = int(desired_width * aspect_ratio)
    cover_img = cover_img.resize((desired_width, desired_height), Image.Resampling.LANCZOS)

        # Step 2: Center the resized cover image on the poster
    cover_x = (poster_width - desired_width) // 2
    cover_y = 80

    # Step 2.1: Create shadow
    shadow_offset = 25
    shadow = Image.new("RGBA", (desired_width + shadow_offset, desired_height + shadow_offset), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle(
        [shadow_offset, shadow_offset, desired_width + shadow_offset, desired_height + shadow_offset],
        fill=(0, 0, 0, 70)  # semi-transparent shadow
    )

    # Blur the shadow slightly (optional, for soft shadow)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=6))

    # Paste the shadow on the poster
    poster.paste(shadow, (cover_x - shadow_offset // 2, cover_y - shadow_offset // 2), shadow)

    # Paste the book cover on top of the shadow
    poster.paste(cover_img, (cover_x, cover_y))


    # Step 3: Draw separator
    draw = ImageDraw.Draw(poster)
    separator_y = cover_y + cover_img.height + 40
    draw.line([(40, separator_y), (poster_width - 40, separator_y)], fill="#e4e0d8", width=2)

    # Fonts
    title_font = ImageFont.truetype(TITLE_FONT, 30)
    sub_font = ImageFont.truetype(TEXT_FONT, 20)
    small_font = ImageFont.truetype(TEXT_FONT, 18)

    # Metadata
    title = book_info["title"]
    authors = book_info["author"]
    year = book_info["year"]
    genre = book_info["genre"]

    text_y = separator_y + 20
    margin_x = 40

    max_width = poster_width - 2 * margin_x
    wrapped_title = textwrap.wrap(title.upper(), width=30)  # Adjust width as needed

    for line in wrapped_title:
        bbox = title_font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        draw.text((margin_x, text_y), line, font=title_font, fill="black")
        text_y += line_height + 5  # Line spacing
    text_y += 10
    draw.text((margin_x, text_y), f"by {authors}", font=sub_font, fill="black")
    text_y += 30
    draw.text((margin_x, text_y), f"genre: {year}", font=small_font, fill="black")
    text_y += 25
    if genre:
        draw.text((margin_x, text_y), f"completed on: {genre}", font=small_font, fill="black")

    # Rating
    rating = book_info["rating"]
    draw_rating(poster, rating, assets_path="assets")

    # Save
    safe_title = title.replace(" ", "_").replace("/", "_")[:30]
    output_path = f"{safe_title}_poster.jpg"
    poster.save(output_path)
    print(f"Book poster saved as {output_path}")

def main():
    book_info = read_book_data()
    if not book_info:
        return

    cover_img = download_image(book_info["image_url"])
    if not cover_img:
        print("Failed to download cover image.")
        return

    generate_book_poster(book_info, cover_img)

if __name__ == "__main__":
    main()

