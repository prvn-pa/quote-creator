from PIL import Image, ImageDraw, ImageFont
import requests
import random
import textwrap

# create image object with random background
img_url = requests.get('https://picsum.photos/800/800').url
img = Image.open(requests.get(img_url, stream=True).raw)
    
# function to draw text on image
def draw_text(text, subtext):
    # get font sizes based on image size
    width, height = img.size
    font_size = int(width / 25)
    subtext_font_size = int(font_size / 1.5)
    
    image_bg = Image.new('RGB', (width, height), color=(255, 255, 255))
    
    # set fonts
    font = ImageFont.truetype('./fonts/TiroTamil-Regular.ttf', font_size)
    subtext_font = ImageFont.truetype('./fonts/Kavivanar-Regular.ttf', subtext_font_size)

    # create draw object
    draw = ImageDraw.Draw(image_bg)
    
    # calculate text position to center it horizontally
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2
    
    # calculate subtext position to center it horizontally and put it below the main text
    subtext_bbox = draw.textbbox((0, 0), subtext, font=subtext_font)
    subtext_width = subtext_bbox[2] - subtext_bbox[0]
    subtext_height = subtext_bbox[3] - subtext_bbox[1]
    subtext_x = (width - subtext_width) / 2
    subtext_y = text_y + text_height + subtext_font_size
    
    # draw text
    draw.text((text_x, text_y - 100), text, font=font, align="center", spacing=20, fill=(0, 0, 0))
    draw.text((subtext_x, subtext_y + 100), subtext, font=subtext_font, fill=(0, 0, 0))
    
    return image_bg

# test the function
with open('tam-sample.txt', 'r') as file:
    # read the first line and assign to x
    main_text = file.readline().strip()
    # read the second line and assign to y
    subtext = file.readline().strip()

# creat image
wrapper = textwrap.TextWrapper(width=30)
main_text = wrapper.fill(main_text)  
image_bg = draw_text(main_text, subtext)

# uncomment the below line if you want to create plain image without unsplash photo
#image_bg.save('quote2.png')

# blend the text image with the downloaded image
blended_image = Image.blend(img, image_bg, alpha=0.5)

# save the final image
blended_image.save('tam-image.jpg')
