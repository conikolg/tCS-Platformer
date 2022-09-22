import pygame


def auto_crop(images: list[pygame.Surface], size: tuple = None) -> list[pygame.Surface]:
    """

    :param images:
    :param size:
    :return:
    """

    # Create mask of all occupied pixels
    occupied_pixels = pygame.mask.Mask(size=images[0].get_size(), fill=False)
    for image in images:
        occupied_pixels.draw(pygame.mask.from_surface(image), offset=(0, 0))
    # Find rectangles defining components of the mask
    bounding_rectangles: list[pygame.Rect] = list(occupied_pixels.get_bounding_rects())
    # Merge into single bounding box
    bounding_rect: pygame.Rect = bounding_rectangles[0].unionall(bounding_rectangles[1:])
    # Crop images
    images: list[pygame.Surface] = [image.subsurface(bounding_rect) for image in images]

    # Scale if requested
    if size is not None:
        images: list[pygame.Surface] = [pygame.transform.scale(image, size) for image in images]

    return images
