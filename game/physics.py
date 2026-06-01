"""Pure movement + collision resolution. No display required."""
import pygame


def move_and_collide(entity, solids):
    """Apply entity.vx/vy to entity.x/y, resolving collisions one axis at a time.

    `entity` must expose floats x, y, vx, vy and ints w, h (top-left box).
    `solids` is an iterable of pygame.Rect. Mutates `entity` in place.
    Returns contacts dict: {'left','right','top','bottom'} -> bool.
    'bottom' True means the entity is standing on something.
    """
    contacts = {"left": False, "right": False, "top": False, "bottom": False}

    # --- X axis ---
    entity.x += entity.vx
    rect = pygame.Rect(round(entity.x), round(entity.y), entity.w, entity.h)
    for s in solids:
        if rect.colliderect(s):
            if entity.vx > 0:
                rect.right = s.left
                contacts["right"] = True
            elif entity.vx < 0:
                rect.left = s.right
                contacts["left"] = True
            entity.x = float(rect.x)
    if contacts["left"] or contacts["right"]:
        entity.vx = 0.0

    # --- Y axis ---
    entity.y += entity.vy
    rect = pygame.Rect(round(entity.x), round(entity.y), entity.w, entity.h)
    for s in solids:
        if rect.colliderect(s):
            if entity.vy > 0:
                rect.bottom = s.top
                contacts["bottom"] = True
            elif entity.vy < 0:
                rect.top = s.bottom
                contacts["top"] = True
            entity.y = float(rect.y)
    if contacts["top"] or contacts["bottom"]:
        entity.vy = 0.0

    return contacts
