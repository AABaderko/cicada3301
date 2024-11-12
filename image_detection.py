from itertools import product
from PIL import Image, ImageChops

from place_data import places_data

def summarise(img):
    resized = img.resize((64, 64))
    return resized

def difference(img1, img2):
    diff = ImageChops.difference(img1, img2)

    acc = 0
    width, height = diff.size
    for w, h in product(range(width), range(height)):
        r, g, b = diff.getpixel((w, h))
        acc += (r + g + b) / 3
    
    average_diff = acc / (width * height)
    normalised_diff = average_diff / 255
    return normalised_diff

def found_img_in_database(img):
    diffs = []
    img_sum = summarise(img)

    for obj in places_data:
        obj_img = Image.open(obj.get('img'))
        obj_img_sum = summarise(obj_img)

        diffs.append(difference(img_sum, obj_img_sum))
    
    for idx, diff in enumerate(diffs):
        if diff < 0.1:
            return idx
    return None

if __name__ == "__main__":
    found_img_in_database(Image.open('place_photos/domGRES2.jpg'))