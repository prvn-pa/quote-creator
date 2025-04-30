import os
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Paths to fonts on your system
TITLE_FONT = "TiroTamil-Regular.ttf"
TEXT_FONT = "NotoSansTamil-Regular.ttf"

def search_books(query, max_results=5):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}"
    resp = requests.get(url)
    return resp.json().get("items", [])

def format_book_info(book):
    info = book.get("volumeInfo", {})
    title = info.get("title", "Unknown Title")
    authors = ", ".join(info.get("authors", []))
    year = info.get("publishedDate", "N/A")[:4]
    return f"{title} by {authors} ({year})"

def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except Exception:
        pass
    return None

#def crop_center_square(image):
    #width, height = image.size
    #min_dim = min(width, height)
   # left = (width - min_dim) // 2
    #top = (height - min_dim) // 2
   #f return image.crop((left, top, left + min_dim, top + min_dim))

def get_user_rating():
    while True:
        try:
            rating = float(input("Your rating (0 to 5, halves allowed): "))
            if 0 <= rating <= 5:
                return rating
        except ValueError:
            pass
        print("Enter a number between 0 and 5.")

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

def generate_book_poster(book, cover_img):
    poster_width, poster_height = 640, 960
    poster = Image.new("RGB", (poster_width, poster_height), color="#e4e0d8")

    # Step 1: Resize cover image to width = 400 while maintaining aspect ratio
    desired_width = 400
    orig_w, orig_h = cover_img.size
    aspect_ratio = orig_h / orig_w
    desired_height = int(desired_width * aspect_ratio)
    cover_img = cover_img.resize((desired_width, desired_height), Image.Resampling.LANCZOS)

    # Step 2: Center the resized cover image on the poster
    cover_x = (poster_width - desired_width) // 2
    cover_y = 80
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
    info = book.get("volumeInfo", {})
    title = info.get("title", "Untitled")
    authors = ", ".join(info.get("authors", []))
    year = info.get("publishedDate", "")[:4]
    genre = ", ".join(info.get("categories", []))

    text_y = separator_y + 20
    margin_x = 40

    draw.text((margin_x, text_y), title.upper(), font=title_font, fill="black")
    text_y += 40
    draw.text((margin_x, text_y), f"by {authors}", font=sub_font, fill="black")
    text_y += 30
    draw.text((margin_x, text_y), f"published: {year}", font=small_font, fill="black")
    text_y += 25
    if genre:
        draw.text((margin_x, text_y), f"genre: {genre}", font=small_font, fill="black")

    # Rating
    rating = get_user_rating()
    draw_rating(poster, rating, assets_path="assets")

    # Save
    safe_title = title.replace(" ", "_").replace("/", "_")[:30]
    output_path = f"{safe_title}_poster.jpg"
    poster.save(output_path)
    print(f"Book poster saved as {output_path}")

def main():
    query = input("Enter book title: ")
    results = search_books(query)

    if not results:
        print("No books found.")
        return

    print("\nSelect the correct book:")
    for idx, book in enumerate(results):
        print(f"{idx + 1}: {format_book_info(book)}")

    try:
        choice = int(input("Enter choice number: ")) - 1
        book = results[choice]
    except Exception:
        print("Invalid choice.")
        return

    info = book.get("volumeInfo", {})
    image_links = info.get("imageLinks", {})
    preferred_keys = ["extraLarge", "large", "medium", "small", "thumbnail", "smallThumbnail"]
    image_url = next((image_links.get(k) for k in preferred_keys if image_links.get(k)), None)


    if not image_url:
        print("No cover image available.")
        return

    cover_img = download_image(image_url)
    if not cover_img:
        print("Failed to download cover.")
        return

    #cover_img = crop_center_square(cover_img)
    generate_book_poster(book, cover_img)

if __name__ == "__main__":
    main()

