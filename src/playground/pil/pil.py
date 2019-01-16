from PIL import Image
import sys

# consider numbers between 0 ~ 999
def fill_3_digits(num):
    if num < 0:
        print("input number of function fill_3_digits(num) should be in range 0 ~ 999")
        return
    if num < 10:
        return "  " + str(num)
    elif num < 100:
        return " " + str(num)
    elif num < 1000:
        return str(num)
    else:
        print("input number of function fill_3_digits(num) should be in range 0 ~ 999")
        return

def show_pixel_map(img_path):
    img = Image.open(img_path)
    width = img.width
    height = img.height

    print("------------------")
    print("Image width: " + str(width))
    print("Image height: " + str(height))
    print("------------------")

    data = list(img.getdata())

    for i in range(img.width):
        sys.stdout.write(fill_3_digits(data[i*width]))
        for j in range(1, img.height):
            # adds a blank before the number
            sys.stdout.write(" " + fill_3_digits(data[i*width + j]))
        sys.stdout.write("\n")

    img.close()

show_pixel_map("1.png")
