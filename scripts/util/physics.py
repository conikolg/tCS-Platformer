import pygame


def get_collision_side(r1: pygame.rect.Rect, r2: pygame.rect.Rect) -> str:
    """
    Determines which side of r2 is primarily responsible for the collision between r1 and r2.

    :param r1: a pygame.rect.Rect object that "has been collided with" r2.
    :param r2: a pygame.rect.Rect object that "did the colliding with" r1.
    :return: a str indicating which side of r2 is colliding the most.
    """

    dx = r1.centerx - r2.centerx
    dy = r1.centery - r2.centery
    width = (r1.w + r2.w) / 2
    height = (r1.h + r2.h) / 2
    cross_width = width * dy
    cross_height = height * dx

    if abs(dx) <= width and abs(dy) <= height:
        if cross_width > cross_height:
            return "bottom" if (cross_width > -cross_height) else "left"
        else:
            return "right" if (cross_width > -cross_height) else "top"
    else:
        raise Exception("Rectangles must be colliding.")
