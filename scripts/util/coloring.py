import pygame


def shift_color(img: pygame.Surface = None, color_shift: int = 0):
    # Get the pixels
    pixels = pygame.PixelArray(img)
    # Iterate over every pixel
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            # Turn the pixel data into an RGB tuple
            rgb = img.unmap_rgb(pixels[x][y])
            # Get a new color object using the RGB tuple and convert to HSLA
            color = pygame.Color(*rgb)
            h, s, l, a = color.hsla
            # Add 120 to the hue (or however much you want) and wrap to under 360
            color.hsla = (int(h) + color_shift) % 360, int(s), int(l), int(a)
            # Assign directly to the pixel
            pixels[x][y] = color
    # The old way of closing a PixelArray object
    del pixels


def recolor(img: pygame.Surface, old_color: tuple = None, new_color: tuple = None):
    new_img = pygame.PixelArray(img)
    new_img.replace(old_color, new_color)
    del new_img
