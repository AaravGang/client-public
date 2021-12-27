import pygame as pg
from constants import *


class Button(object):
    """A fairly straight forward button class."""

    def __init__(
        self, rect, color, function, truncate=True, id=None, tags=(), **kwargs
    ):
        self.rect = pg.Rect(rect)
        self.real_rect = None
        self.color = color
        self.function = function
        self.clicked = False
        self.hovered = False
        self.hover_text = None
        self.clicked_text = None
        self.disabled = False
        self.disabled_color = Colors.GRAY
        self.disabled_text_color = Colors.WHITE
        self.truncate = truncate
        self.process_kwargs(kwargs)
        self.render_text()
        self.highlight_color = None
        self.id = id
        self.tags = tags
        self.tag_surfs = []  # [(surface,rect),...]
        self.create_tags()

    def process_kwargs(self, kwargs):
        """Various optional customization you can change by passing kwargs."""
        settings = {
            "font": pg.font.Font(None, 16),
            "text": None,
            "call_on_release": True,
            "hover_color": None,
            "clicked_color": None,
            "font_color": pg.Color("white"),
            "hover_font_color": None,
            "clicked_font_color": None,
            "click_sound": None,
            "hover_sound": None,
            "border_radius": 0,
            "on_popup_close": None,
            "hover_image": None,
            "image": None,
        }
        if kwargs.get("font"):
            settings["font"] = kwargs["font"]

        for kwarg in kwargs:
            if kwarg == "text" and self.truncate:
                if settings["font"].size(kwargs["text"])[0] > self.rect.width:
                    while (
                        settings["font"].size(kwargs["text"] + "...")[0]
                        > self.rect.width
                    ):
                        kwargs["text"] = kwargs["text"][:-1]
                    kwargs["text"] += "..."

            settings[kwarg] = kwargs[kwarg]

        self.__dict__.update(settings)

    def create_tags(self):
        x, y = self.rect.x +5, self.rect.y +5
        font = Fonts.small_font
        for tag in self.tags:
            text_surf = font.render(tag, True, Colors.BLACK)
            rect = text_surf.get_rect(topleft=(x, y))
            x += rect.width + 10
            self.tag_surfs.append((text_surf, rect))

    def render_text(self):
        """Pre render the button text."""

        if self.text:
            if self.disabled:
                self.rendered_text = self.font.render(
                    self.text, True, self.disabled_text_color
                )

            else:
                if self.hover_font_color:
                    color = self.hover_font_color
                    self.hover_text = self.font.render(self.text, True, color)
                if self.clicked_font_color:
                    color = self.clicked_font_color
                    self.clicked_text = self.font.render(self.text, True, color)
                self.rendered_text = self.font.render(self.text, True, self.font_color)

    def check_event(self, event, **kwargs):
        """The button needs to be passed events from your program event loop."""
        if self.disabled:
            self.clicked = False
            self.hovered = False

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            return self.on_click(event, **kwargs)
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            return self.on_release(event, **kwargs)

        self.check_hover()

    def on_click(self, event, **kwargs):
        if self.real_rect and self.real_rect.collidepoint(event.pos):
            self.clicked = True
            if not self.call_on_release:
                return self.function(
                    button=self, on_close=self.on_popup_close, **kwargs
                )
        elif not self.real_rect and self.rect.collidepoint(event.pos):
            self.clicked = True
            if not self.call_on_release:
                return self.function(
                    button=self, on_close=self.on_popup_close, **kwargs
                )

    def on_release(self, event, **kwargs):
        return_val = None
        if self.clicked and self.call_on_release:
            return_val = self.function(
                button=self, on_close=self.on_popup_close, **kwargs
            )
            if saved_settings["sound_effects"] and self.click_sound:
                self.click_sound.play()
        self.clicked = False
        return return_val

    def check_hover(self):

        if self.real_rect and self.real_rect.collidepoint(pg.mouse.get_pos()):
            if not self.hovered:
                self.hovered = True
                if self.hover_sound:
                    self.hover_sound.play()
        elif not self.real_rect and self.rect.collidepoint(pg.mouse.get_pos()):

            if not self.hovered:
                self.hovered = True
                if self.hover_sound:
                    self.hover_sound.play()
        else:

            self.hovered = False

    def disable(self):
        self.disabled = True
        self.render_text()

    def change_text(self, text):
        self.text = text
        self.render_text()

    def set_highlight(self, color):
        self.highlight_color = color

    def enable(self):
        self.disabled = False
        self.render_text()

    def update(self, surface):
        """Update needs to be called every frame in the main loop."""
        color = self.disabled_color if self.disabled else self.color
        render_text = None
        if self.text:
            render_text = self.rendered_text

        if self.disabled:
            pass

        elif self.clicked and self.clicked_color:
            color = self.clicked_color
            if self.clicked_font_color and self.text:
                render_text = self.clicked_text

        elif self.hovered and self.hover_color:
            color = self.hover_color
            if self.hover_font_color and self.text:
                render_text = self.hover_text

        if self.highlight_color:
            color = self.highlight_color
        # surface.fill(pg.Color("black"),self.rect)
        # surface.fill(color,self.rect.inflate(-4,-4))

        pg.draw.rect(surface, Colors.BLACK, self.rect, border_radius=self.border_radius)
        pg.draw.rect(
            surface,
            color,
            (self.rect.inflate(-4, -4)),
            border_radius=self.border_radius,
        )

        if self.image is not None:
            image_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, image_rect)

        if self.hovered and self.hover_image:
            image_rect = self.hover_image.get_rect(center=self.rect.center)
            surface.blit(self.hover_image, image_rect)

        if self.text and render_text:
            text_rect = render_text.get_rect(center=self.rect.center)
            surface.blit(render_text, text_rect)

        for s, r in self.tag_surfs:
            pg.draw.rect(
                surface, Colors.PURPLE, r.inflate(5, 5), border_radius=2,
            )
            surface.blit(s, r)

