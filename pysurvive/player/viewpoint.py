import pygame as pg

from pysurvive.config import COLORKEY, RED


class Viewpoint(pg.sprite.Sprite):

    """Represents the signs / mouse cursor of the player."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.color = RED
        self.size = 10
        self.image = pg.Surface((self.size, self.size))
        self.image.fill(COLORKEY)
        self.image.set_colorkey(COLORKEY)
        self.rect = pg.Rect(self.x, self.y, self.size, self.size)
        self._render()

    @property
    def pos(self) -> tuple[int, int]:
        """Get the x, y coordinate of the mouse cursor."""
        return pg.mouse.get_pos()

    @property
    def x(self) -> int:
        """Get the x coordinate of the mouse cursor."""
        x, _ = self.pos
        return x

    @property
    def y(self) -> int:
        """Get the y coordinate of the mouse cursor."""
        _, y = self.pos
        return y

    def _render(self) -> None:
        """
        Render initial a cross as mouse cursor on
        its own surface to blit it later at once.
        """
        pg.draw.line(
            self.image,
            self.color,
            (1, 1),
            (self.size, self.size),
        )
        pg.draw.line(
            self.image,
            self.color,
            (0, self.size),
            (self.size, 0),
        )

    def update(self) -> None:
        """Update the player viewpoint cursor positon."""
        self.rect.centerx = self.x
        self.rect.centery = self.y
