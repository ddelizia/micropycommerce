import os


def resize_image(file_path):
    from wand.image import Image

    with Image(filename=file_path) as img:
        with img.clone() as i:
            i.format = 'jpeg'
            i.resize(int(i.width * 0.5), int(i.height * 0.5))
            i.save(filename='/tmp/tmp.jpg')

    return '/tmp/tmp.jpg'


def file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return file_info.st_size


def resize_image_when_greater_than(file_path, size):
    f_s = file_size(file_path)
    if f_s > size:
        return resize_image(file_path)
    else:
        return file_path
