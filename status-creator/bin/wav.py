import math
import random
from datetime import datetime
from PIL import Image, ImageDraw

# Canvas settings
WIDTH, HEIGHT = 2560, 1440

# Pastel colors
PASTEL_COLORS = [
    (62, 33, 97), (137, 79, 166), (203, 78, 145),
    (245, 121, 148), (246, 132, 178), (244, 98, 108),
    (182, 97, 184), (71, 88, 153), (110, 98, 157)
]

def draw_wave(draw, y_offset, amplitude, frequency, phase, color, height, width):
    points = []
    for x in range(0, width + 10, 5):
        y = y_offset + amplitude * math.sin(frequency * x + phase)
        points.append((x, y))
    # Close the shape down to the bottom
    points += [(width, height), (0, height)]
    draw.polygon(points, fill=color)

def generate_wavy_art(width=1000, height=1000, layers=5):
    bg_color = tuple(random.randint(240, 255) for _ in range(3))
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    base_y = height // 2
    for i in range(layers):
        amp = random.uniform(20, 80)
        freq = random.uniform(0.005, 0.02)
        phase = random.uniform(0, 2 * math.pi)
        y_offset = base_y + (i - layers // 2) * 60 + random.randint(-30, 30)
        color = random.choice(PASTEL_COLORS)
        draw_wave(draw, y_offset, amp, freq, phase, color, height, width)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"wavy_art_{timestamp}.jpg"
    image.save(filename, "JPEG", quality=95)
    print(f"Saved: {filename}")

if __name__ == "__main__":
    generate_wavy_art(WIDTH, HEIGHT)

