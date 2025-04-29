import qrcode
import pyshorteners
from PIL import Image

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
    img = img.resize((50, 50), Image.Resampling.LANCZOS)

    # Save the image as a PNG file
    img.save(output_path, 'PNG')

# Example usage:
generate_qr_code('https://www.scmp.com/news/china/science/article/3308204/former-asml-head-scientist-lin-nan-drives-chinas-latest-euv-breakthrough?module=flexi_unit-focus&pgtype=homepage', 'qr_code.png')

