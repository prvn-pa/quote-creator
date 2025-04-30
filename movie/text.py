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

RATING_TEXT_MAP = {
    0.0: "pathetic",
    0.5: "terrible",
    1.0: "very bad",
    1.5: "bad",
    2.0: "poor",
    2.5: "below average",
    3.0: "average",
    3.5: "good",
    4.0: "very good",
    4.5: "great",
    5.0: "excellent"
}

def get_user_rating():
    while True:
        try:
            rating = float(input("Your rating (0 to 5, can be decimal): "))
            if 0 <= rating <= 5:
                return round(rating * 2) / 2  # round to nearest 0.5
            else:
                print("Please enter a number between 0 and 5.")
        except ValueError:
            print("Invalid input. Try again.")

def draw_rating(draw, rating, font, image_size):
    description = RATING_TEXT_MAP.get(rating, "unrated")
    text = f"My Rating: {description}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (image_size[0] - text_width) // 2
    y = image_size[1] - text_height - 30
    draw.text((x, y), text, font=font, fill="black")

def generate_poster(movie, poster_img):
    width, height = 640, 960
    poster = Image.new("RGB", (width, height), color="#e4e0d8")

    # Resize and paste poster image
    poster_img = poster_img.resize((width, int(height * 0.7)))
    poster.paste(poster_img, (0, 0))

    draw = ImageDraw.Draw(poster)

    title_font = ImageFont.truetype(TITLE_FONT, 36)
    sub_font = ImageFont.truetype(TEXT_FONT, 20)
    small_font = ImageFont.truetype(TEXT_FONT, 18)

    y = int(height * 0.7) + 20
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

    if 'producer' in movie:
        draw.text((20, y), f"produced by:  {format_list(movie['producer'])}", font=small_font, fill="black")
        y += 30

    if 'cast' in movie:
        draw.text((20, y), f"starring:  {format_list(movie['cast'])}", font=small_font, fill="black")

    # Ask and draw rating
    rating = get_user_rating()
    draw_rating(draw, rating, small_font, poster.size)

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

