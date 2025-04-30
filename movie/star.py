import os
import sys
import requests
from imdb import IMDb
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Fonts (update these with paths to TTF fonts on your system)
TITLE_FONT = "TiltWarp-Regular.ttf"
TEXT_FONT = "Poppins-Regular.ttf"

def download_poster(url):
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        return None

def format_list(names, max_len=3):
    return ", ".join([p['name'] for p in names[:max_len]])

def get_highres_url(url):
    if "_V1_" in url:
        base = url.split("_V1_")[0]
        ext = url.split('.')[-1]
        return f"{base}_V1_.{ext}"
    return url

def crop_center_square(image):
    width, height = image.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    return image.crop((left, top, right, bottom))

def get_user_rating():
    while True:
        try:
            rating = float(input("Your rating (0 to 5, half-stars allowed): "))
            if 0 <= rating <= 5:
                return rating
            else:
                print("Please enter a number between 0 and 5.")
        except ValueError:
            print("Invalid input. Try again.")

def get_star_icons(rating, assets_path="assets"):
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    icons = []
    icons += ["star_full.png"] * full_stars
    icons += ["star_half.png"] * half_star
    icons += ["star_empty.png"] * empty_stars

    return [Image.open(os.path.join(assets_path, icon)).convert("RGBA") for icon in icons]

def draw_rating(poster_img, rating, assets_path="assets", spacing=10, y_offset=30, label_font_path=TEXT_FONT):
    """
    Draws star icons at the bottom center of the poster image.
    """
    stars = get_star_icons(rating, assets_path)
    if not stars:
        return
        
    draw = ImageDraw.Draw(poster_img)
    label_font = ImageFont.truetype(label_font_path, 16)

    star_width, star_height = stars[0].size
    total_width = len(stars) * star_width + (len(stars) - 1) * spacing

        # Text position
    label_text = "My Rating:"
    label_bbox = draw.textbbox((0, 0), label_text, font=label_font)
    label_width = label_bbox[2] - label_bbox[0]
    label_height = label_bbox[3] - label_bbox[1]
    label_x = (poster_img.width - label_width) // 2
    label_y = poster_img.height - star_height - y_offset - label_height - 10

    draw.text((label_x, label_y), label_text, font=label_font, fill="black")

    # Stars below the text
    x_start = (poster_img.width - total_width) // 2
    y_start = label_y + label_height + 15  # a little gap between text and stars

    for i, star in enumerate(stars):
        x = x_start + i * (star_width + spacing)
        poster_img.paste(star, (x, y_start), star)


def generate_poster(movie, poster_img):
    width, height = 640, 960
    poster = Image.new("RGB", (width, height), color="#e4e0d8")

    # Resize and paste poster image
    poster_img = poster_img.resize((width, int(height * 0.715)))
    poster.paste(poster_img, (0, 0))

    draw = ImageDraw.Draw(poster)

    title_font = ImageFont.truetype(TITLE_FONT, 36)
    sub_font = ImageFont.truetype(TEXT_FONT, 20)
    small_font = ImageFont.truetype(TEXT_FONT, 18)

    y = int(height * 0.715) + 20
    draw.text((20, y), f"{movie['title'].upper()}", font=title_font, fill="black")
    y += 40
    draw.text((20, y), f"{movie.get('year', '')}", font=sub_font, fill="black")
    y += 40

    genre = ", ".join(movie.get('genres', []))
    draw.text((20, y), f"genre:  {genre}", font=small_font, fill="black")
    y += 30

    if 'director' in movie:
        draw.text((20, y), f"directed by:  {format_list(movie['director'])}", font=small_font, fill="black")
        y += 30

    if 'cast' in movie:
        draw.text((20, y), f"starring:  {format_list(movie['cast'])}", font=small_font, fill="black")

    # Ask and draw rating
    rating = get_user_rating()
    draw_rating(poster, rating, assets_path="assets")

    # Save final image
    movie_title = movie['title'].replace(" ", "_")
    output_path = f"{movie_title}_poster.jpg"
    poster.save(output_path)
    print(f"Poster saved as {output_path}")

def main():
    ia = IMDb()
    query = input("Enter movie name: ")
    search_results = ia.search_movie(query)

    if not search_results:
        print("No movies found.")
        return

    print("\nSelect the correct movie:")
    for idx, movie in enumerate(search_results[:5]):
        ia.update(movie, info=['main'])  # Fetch main data including 'year'
        title = movie.get('title', 'Unknown Title')
        year = movie.get('year', 'Unknown Year')
        print(f"{idx + 1}: {title} ({year})")

    choice = int(input("Enter choice number: ")) - 1
    movie = search_results[choice]
    ia.update(movie, info=['main', 'full credits'])

    if 'cover url' not in movie:
        print("No poster available for this movie.")
        return

    highres_url = get_highres_url(movie['cover url'])
    poster_img = download_poster(highres_url)
    if not poster_img:
        print("Failed to download poster image.")
        return

    poster_img = crop_center_square(poster_img)
    generate_poster(movie, poster_img)

if __name__ == "__main__":
    main()

