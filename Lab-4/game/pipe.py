import pygame
import random

class Pipe:
    def __init__(self, x, screen_height, gap=150, width=70, speed=4):
        self.x = x
        self.width = width
        self.gap = gap
        self.speed = speed
        self.screen_height = screen_height
        self.gap_y = random.randint(100, screen_height - 100 - gap)
        self.scored = False

    def move(self):
        self.x -= self.speed

    def off_screen(self):
        return self.x + self.width < 0

    def top_rect(self):
        return pygame.Rect(self.x, 0, self.width, self.gap_y)

    def bottom_rect(self):
        bottom_y = self.gap_y + self.gap
        return pygame.Rect(self.x, bottom_y, self.width, self.screen_height - bottom_y)

    def collides_with_circle(self, cx, cy, radius):
        """True if a circle (the bird) overlaps either pipe segment.

        Uses exact circle-vs-rectangle maths on the float positions instead
        of a single centre point, so grazing an edge or corner counts.
        """
        bottom_y = self.gap_y + self.gap
        segments = (
            (self.x, 0, self.x + self.width, self.gap_y),                    # top pipe
            (self.x, bottom_y, self.x + self.width, self.screen_height),     # bottom pipe
        )
        for left, top, right, bottom in segments:
            # Closest point on the rectangle to the circle's centre
            nearest_x = max(left, min(cx, right))
            nearest_y = max(top, min(cy, bottom))
            dx, dy = cx - nearest_x, cy - nearest_y
            if dx * dx + dy * dy <= radius * radius:
                return True
        return False
