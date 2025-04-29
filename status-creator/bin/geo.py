import random
from PIL import Image, ImageDraw
from datetime import datetime

# Canvas size (can be changed)
WIDTH, HEIGHT = 1000, 1000

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

def generate_geometric_art(width=1000, height=1000, max_shapes=5):
    bg_color = tuple(random.randint(240, 255) for _ in range(3)) + (255,)
    image = Image.new('RGBA', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image, 'RGBA')

    for _ in range(random.randint(3, max_shapes)):
        shape = random.choice(SHAPES)
        color = get_translucent_color()
        size = random.randint(width // 3, int(width / 1.5))
        x = random.randint(-size // 4, width - size // 2)
        y = random.randint(-size // 4, height - size // 2)
        draw_shape(draw, shape, x, y, size, color)

    # Convert to RGB and save
    final_image = image.convert('RGB')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"geometric_art_{timestamp}.jpg"
    final_image.save(filename, "JPEG", quality=95)
    print(f"Saved: {filename}")

if __name__ == "__main__":
    generate_geometric_art(WIDTH, HEIGHT)

