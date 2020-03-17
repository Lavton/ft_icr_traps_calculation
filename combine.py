from PIL import Image
from matplotlib.pyplot import imshow

import plot_trap_3d
import comet_calculator
# from matplotlib import imshow
_IMAGE_LOCATION = r"C:\Users\Anton.Lioznov\YandexDisk\work\Skoltech\2019\Marchall\images\combined"


def combine_pics(trap_name, with_contour=False, show=False):
    """Combine 3d visualization and 2D plots into 1 picture"""
    image_3d = Image.open(f"{plot_trap_3d._3D_IMAGE_LOCATION}\\{trap_name}.png")
    image_2d = Image.open(f"{comet_calculator._2D_IMAGE_LOCATION}\\{trap_name}.png")
    image_contour = None
    if with_contour:
        image_contour = Image.open(f"{comet_calculator._2D_IMAGE_LOCATION}\\{trap_name}_contour.png")
        image_contour = image_contour.rotate(-90, expand=True)
    width = image_2d.size[0] + image_3d.size[0]
    if image_contour:
        width += image_contour.size[0]
    new_image = Image.new("RGB", (width, image_3d.size[1]), color="white")
    new_image.paste(image_3d, (0, 0))
    new_image.paste(image_2d, (image_3d.size[0], 0))
    if image_contour:
        new_image.paste(image_contour, (image_2d.size[0] + image_3d.size[0], 0))
    if show:
        new_image.show()
    new_image.save(f"{_IMAGE_LOCATION}\\{trap_name}.png")


def combine_3d_and_contour(trap_name, show=True):
    image_3d = Image.open(f"{plot_trap_3d._3D_IMAGE_LOCATION}\\{trap_name}.png")
    image_contour = Image.open(f"{comet_calculator._2D_IMAGE_LOCATION}\\{trap_name}_contour.png")
    print(image_3d.size, image_contour.size)
    w, h = image_contour.size
    delta = int(0 / 4 * ((w-80)/h))
    width = image_3d.size[0] + image_contour.size[0] - delta * 2
    new_image = Image.new("RGB", (width, image_3d.size[1]), color="white")
    new_image.paste(image_3d, (0, 0))
    new_image.paste(image_contour.crop((delta, 0, w-delta, h)), (image_3d.size[0], 0))
    im_name = f"{_IMAGE_LOCATION}\\{trap_name}_vis.png"
    new_image.save(im_name)
    if show:
        imshow(new_image)
