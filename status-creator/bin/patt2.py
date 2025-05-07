import math
import random
from datetime import datetime
from PIL import Image, ImageDraw

# Canvas settings
WIDTH, HEIGHT = 2560, 1440

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
    (17, 42, 53),     # Deep Teal
    (68, 87, 104),    # Slate Blue-Green
    (193, 103, 88),   # Warm Coral
    (12, 26, 34),     # Midnight Blue
    (34, 73, 91),     # Ocean Slate
    (244, 147, 97),   # Sunset Peach
    (103, 120, 121),  # Steel Gray
    (124, 161, 161),  # Soft Aqua
    (46, 52, 59)      # Charcoal Teal
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

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"wavy_art_{timestamp}.jpg"
    image.save(filename, "JPEG", quality=95)
    print(f"Saved: {filename}")

if __name__ == "__main__":
    generate_wavy_background(WIDTH, HEIGHT)

