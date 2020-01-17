from PIL import Image
import plot_trap_3d
import comet_calculator
_IMAGE_LOCATION = r"C:\Users\Anton.Lioznov\YandexDisk\work\Skoltech\2019\Marchall\images\combined"


def combine_pics(trap_name, show=False):
    """Combine 3d visualization and 2D plots into 1 picture"""
    image_3d = Image.open(f"{plot_trap_3d._3D_IMAGE_LOCATION}\\{trap_name}.png")
    image_2d = Image.open(f"{comet_calculator._2D_IMAGE_LOCATION}\\{trap_name}.png")
    new_image = Image.new("RGB", (image_2d.size[0] + image_3d.size[0], image_3d.size[1]), color="white")
    new_image.paste(image_3d, (0, 0))
    new_image.paste(image_2d, (image_3d.size[0], 0))
    if show:
        new_image.show()
    new_image.save(f"{_IMAGE_LOCATION}\\{trap_name}.png")