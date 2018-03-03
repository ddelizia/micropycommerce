import glob
import os

from shutil import copy2

from modules.image_service import resize_image_when_greater_than
images = glob.glob("/Users/ddelizia/Downloads/varianti/*_*")

for image in images:
    file_name = os.path.basename(image)
    image_path = resize_image_when_greater_than(image, 3e+6)
    copy2(image_path, "/Users/ddelizia/Downloads/varianti/new/{0}".format(file_name))