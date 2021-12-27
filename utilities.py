from constants import *
import pygame
from button import Button
from animated_backgrounds import FireworksWindow, FloatersWindow
import random
import pyperclip, json, time
import numpy as np

# print(pygame.__version__)  # has to be 2.0.0.dev8
# pygame.init()

celebrations = [FireworksWindow]
mourns = [FloatersWindow]

# the user button displayed on home screen
class UserButton:
    def __init__(
        self,
        id,
        x,
        y,
        w,
        h,
        page,
        row,
        col,
        color,
        text,
        curr_user,
        on_click,
        image=None,
        bot=False,
    ):
        self.curr_user = curr_user
        self.bot = bot

        self.w, self.h = w, h
        self.on_click = on_click
        self.color = color
        self.rect = pygame.Rect((x, y, w, h))
        self.username = text
        self.image = pygame.surfarray.make_surface(image) if image is not None else None

        self.button_style = Button_Styles.USER_BUTTON_STYLE.copy()
        self.avg_color = self.color
        self.text_color = [
            255 - c for c in self.avg_color
        ]  # create a stand out text color

        self.button_style["font_color"] = self.text_color

        self.button_style["tags"] = ["YOU"] if self.curr_user else []
        if self.bot:
            self.button_style["tags"].append("BOT")

        self.button = Button(
            self.rect,
            self.color,
            self.click,
            text=self.username,
            image=self.image,
            **self.button_style,
        )
        self.id = id
        self.row, self.col, self.page = row, col, page

    def check_event(self, e):
        self.button.check_event(e)

    def click(self, **kwargs):
        self.on_click(self)

    def show(self, win):
        self.button.update(win)

    def update(self, changed: dict):
        self.__dict__.update(changed)
        self.rect = pygame.Rect(self.rect)
        if self.image:
            self.image = pygame.transform.scale(self.image, (int(self.w), int(self.h)))

            text_rect = (
                self.button_style["font"]
                .render(self.username, True, Colors.BLACK)
                .get_rect(center=self.rect.center)
            )

            arr = pygame.surfarray.array3d(self.image)[
                int(text_rect.x - self.rect.x) : int(
                    text_rect.x - self.rect.x + text_rect.width,
                ),
                int(text_rect.y - self.rect.y) : int(
                    text_rect.y - self.rect.y + text_rect.height
                ),
            ]

            avg_color_per_row = np.average(arr, axis=0,)

            self.avg_color = np.round(np.average(avg_color_per_row, axis=0)).astype(
                np.int64
            )

            self.text_color = [
                255 - c for c in self.avg_color
            ]  # create a stand out text color
            self.button_style["font_color"] = self.text_color

        if changed.get("bot") is True:
            self.button_style["tags"].append("BOT")

        self.button = Button(
            self.rect,
            self.color,
            self.click,
            text=self.username,
            image=self.image,
            **self.button_style,
        )


# the cotainer where user buttons appear
class UserButton_Container:
    def __init__(self, title="Home", x=0, y=0, w=LEFT_WIDTH, h=HEIGHT):

        self.x, self.y, self.w, self.h = x, y, w, h

        self.surf = pygame.Surface((self.w, self.h))
        self.title_text = title
        self.title = Fonts.title_font.render(self.title_text, False, Colors.LIGHT_BLUE)
        self.title_rect = self.title.get_rect(center=(self.w // 2, 30))

        # keep trach of the buttons
        self.user_buttons = {}
        # will be a 3d list -> [[[col,col],[col,col],..],...]
        # page -> row -> col
        self.user_buttons_list = [[[]]]

        self.current_page = 0  # display this page at this index

        # buttons to navigate between pages
        self.pagination_buttons = []
        self.pagination_button_height = 50
        self.next = None
        self.prev = None
        self.first = None
        self.create_pagination_buttons()
        self.update_pagination()

        # show which page the user is currently looking at
        self.page_render = Fonts.notification_font.render(
            f"{self.current_page+1}/{len(self.user_buttons_list)}", True, Colors.GRAY
        )
        self.page_render_rect = self.page_render.get_rect(
            center=(
                self.title_rect.x - self.page_render.get_width(),
                self.title_rect.y + self.title_rect.height / 2,
            )
        )

        # the number of rows and columns of user buttons per page
        self.rows = 4
        self.cols = 2

        self.user_button_gap = 20
        # calculate the width and height of the buttons
        self.user_button_w = (self.w - ((self.cols + 1) * (self.user_button_gap))) / (
            self.cols
        )
        self.user_button_h = (
            self.h
            - self.title_rect.height
            - self.pagination_button_height
            - (self.rows + 1) * (self.user_button_gap)
        ) / self.rows

        # display total number of users
        self.num_users = 0  # this is for popups id
        self.num_users_text_center = (
            self.title_rect.x + self.title_rect.width + 30,
            self.title_rect.y + self.title_rect.height / 2,
        )
        self.num_users_text = Fonts.notification_font.render(str(0), True, Colors.WHITE)
        self.num_users_text_rect = self.num_users_text.get_rect(
            center=self.num_users_text_center
        )

        self.updating = False

    def prev_page(self, *args, **kwargs):
        self.current_page -= 1 if self.current_page > 0 else 0
        self.update_pagination()

    def next_page(self, *args, **kwargs):
        self.current_page += (
            1 if self.current_page < len(self.user_buttons_list) - 1 else 0
        )
        self.update_pagination()

    def first_page(self, *args, **kwargs):
        self.current_page = 0
        self.update_pagination()

    def create_pagination_buttons(self):
        self.prev = Button(
            (
                2 * self.w / 3 - 150,
                self.h - self.pagination_button_height,
                50,
                self.pagination_button_height,
            ),
            Colors.ORANGE,
            self.prev_page,
            image=pygame.transform.scale(
                Images.previous, (50, self.pagination_button_height)
            ),
            **Button_Styles.PAGINATION_BUTTON_STYLE,
        )
        self.first = Button(
            (
                self.w / 3 - 100,
                self.h - self.pagination_button_height,
                50,
                self.pagination_button_height,
            ),
            Colors.ORANGE,
            self.first_page,
            image=pygame.transform.scale(
                Images.first, (50, self.pagination_button_height)
            ),
            **Button_Styles.PAGINATION_BUTTON_STYLE,
        )
        self.next = Button(
            (
                self.w - 200,
                self.h - self.pagination_button_height,
                50,
                self.pagination_button_height,
            ),
            Colors.ORANGE,
            self.next_page,
            image=pygame.transform.scale(
                Images.next, (50, self.pagination_button_height)
            ),
            **Button_Styles.PAGINATION_BUTTON_STYLE,
        )
        self.pagination_buttons.extend([self.next, self.prev, self.first])
        self.reposition_buttons()

    def reposition_buttons(self):
        for button in self.pagination_buttons:
            button.real_rect = pygame.Rect(
                self.x + button.rect.x,
                self.y + button.rect.y,
                button.rect.width,
                button.rect.height,
            )

    def update_pagination(self):
        self.prev.disable()
        self.first.disable()
        self.next.disable()

        # next button is available if we are not on the last page
        if self.current_page < len(self.user_buttons_list) - 1:
            self.next.enable()

        # if we are not on the first page, prev and first are available
        if self.current_page > 0:
            self.prev.enable()
            self.first.enable()

        # update the page number
        self.page_render = Fonts.notification_font.render(
            f"{self.current_page+1}/{len(self.user_buttons_list)}", True, Colors.GRAY,
        )

    def add_page(self):
        # add a page with an empty row
        self.user_buttons_list.append([[]])

    def add_row(self):
        # if the number of rows on that page are less that the max rows, then add a row/ []
        # otherwise create a new page
        if len(self.user_buttons_list[-1]) < self.rows:
            self.user_buttons_list[-1].append([])
        else:
            self.add_page()

    def add_user_button(
        self, user, curr_user: bool, on_click,
    ):

        # if the last page's last row already is full, then add a new row or a new page
        if len(self.user_buttons_list[-1][-1]) >= self.cols:
            self.add_row()

        # the page this button will be added to
        page = len(self.user_buttons_list) - 1

        row = (
            len(self.user_buttons_list[page]) - 1
        )  # the index of the last row on the last page
        col = len(
            self.user_buttons_list[page][row]
        )  # the length of the last row, cuz this button hasn't been added yet

        # row -> y cor, col -> x cor

        btn = UserButton(
            user["id"],
            col * (self.user_button_w + self.user_button_gap) + self.user_button_gap,
            self.title_rect.height
            + row * (self.user_button_h + self.user_button_gap)
            + self.user_button_gap,
            self.user_button_w,
            self.user_button_h,
            page,
            row,
            col,
            user["color"],
            str(user["username"]),
            curr_user,
            on_click,
            image=user.get("image"),
            bot=user.get("bot"),
        )

        self.user_buttons[user["id"]] = btn
        self.user_buttons_list[-1][row].append(btn)

        # update the number of users
        self.num_users += 1
        self.update_num_users()
        self.update_pagination()

    def update_num_users(self):
        self.num_users_text = Fonts.notification_font.render(
            str(self.num_users), False, Colors.WHITE
        )
        self.num_users_text_rect = self.num_users_text.get_rect(
            center=self.num_users_text_center
        )

    def shift_user_buttons(self):
        all_buttons = []
        for page in self.user_buttons_list:
            for row in page:
                all_buttons.extend(row)

        self.user_buttons_list = [[[]]]

        while len(all_buttons) > 0:
            # if the last page's last row already is full, then add a new row or a new page
            if len(self.user_buttons_list[-1][-1]) >= self.cols:
                self.add_row()

            btn = all_buttons.pop(0)

            self.user_buttons_list[-1][-1].append(btn)

            row, col = (
                len(self.user_buttons_list[-1]) - 1,
                len(self.user_buttons_list[-1][-1]) - 1,
            )
            btn.update(
                {
                    "page": len(self.user_buttons_list) - 1,
                    "row": row,
                    "col": col,
                    "rect": (
                        col * (self.user_button_w + self.user_button_gap)
                        + self.user_button_gap,
                        self.title_rect.height
                        + row * (self.user_button_h + self.user_button_gap)
                        + self.user_button_gap,
                        self.user_button_w,
                        self.user_button_h,
                    ),
                }
            )

        if self.current_page >= len(self.user_buttons_list):
            self.current_page = len(self.user_buttons_list) - 1

    def remove_user_button(self, id):
        btn = self.user_buttons.pop(id)
        row, col, page = btn.row, btn.col, btn.page

        # remove that button
        self.user_buttons_list[page][row].pop(col)
        self.num_users -= 1

        self.shift_user_buttons()

        # update pagination buttons and also the number of users
        self.update_pagination()
        self.update_num_users()

    def draw(self, win):
        self.surf.fill(Colors.BG_COLOR)
        for row in self.user_buttons_list[self.current_page]:
            for btn in row:
                btn.show(self.surf)

        for button in self.pagination_buttons:
            button.update(self.surf)

        self.surf.blit(self.title, self.title_rect)

        if self.num_users > 0:
            pygame.draw.circle(
                self.surf, Colors.RED, self.num_users_text_center, 15,
            )
            self.surf.blit(self.num_users_text, self.num_users_text_rect)

        self.surf.blit(self.page_render, self.page_render_rect)

        win.blit(self.surf, (self.x, self.y))

    def check_event(self, e):

        for row in self.user_buttons_list[self.current_page]:
            for btn in row:
                btn.check_event(e)

        for button in self.pagination_buttons:
            button.check_event(e)

    def update_button(self, user_id, changed):
        self.user_buttons[user_id].update(changed=changed)


# base class for the challenge button, displayed on a users profile
class ChallengeButton:
    def __init__(self, x, y, w, h, user_id, game, on_click, text=""):
        self.on_click = on_click
        self.button = Button(
            (x, y, w, h),
            Colors.LIGHT_BLUE,
            self.click,
            text=text if len(text) > 0 else f"Challenge: {game}",
            **Button_Styles.CHALLENGE_BUTTON_STYLE,
        )
        self.user_id = user_id  # the user to be challenged
        self.game = game  # which game
        self.disabled = False

    def click(self, **kwargs):

        self.on_click(self.user_id, self.game)
        # self.change_text("CHALLENGE SENT")

    def show(self, win):

        self.button.update(win)

    def check_event(self, e):
        if not self.disabled:
            self.button.check_event(e)

    def enable(self):
        self.button.enable()

    def disable(self):
        self.button.disable()


# base class for a close X button
class Close:
    def __init__(self, x, y, w=50, h=50, on_click=lambda: None):
        self.on_click = on_click
        self.font = pygame.font.SysFont("timesnewroman", round((x + y) / 2), bold=True)
        self.button = Button(
            (x, y, w, h),
            Colors.LIGHT_BLUE,
            self.on_click,
            text="X",
            **Button_Styles.CLOSE_BUTTON_STYLE,
        )
        self.update = self.show

    def show(self, surf):
        self.button.update(surf)

    def check_event(self, e):
        self.button.check_event(e)


# the class container for the profile of a user
class Profile:
    def __init__(
        self,
        user,
        curr_user: bool,
        on_close,
        on_challenge_button_click,
        on_user_name_change=None,
        on_image_change=None,
    ):
        self.w, self.h = LEFT_WIDTH, HEIGHT
        # The title
        self.title = Fonts.user_font.render(user["username"], True, Colors.WHITE)
        self.title_rect = self.title.get_rect(center=(LEFT_WIDTH // 2, 100))

        self.text, self.text_rect = None, None

        self.user = user  # the user details
        self.curr_user = curr_user  # is this the current user?

        self.buttons = {
            "close": [Close(LEFT_WIDTH - 80, 80, 50, 50, on_close)],
            "buttons": [],
        }

        if not self.curr_user:
            # set up the challenge buttons
            # where should the challenge buttons begin?
            self.challenge_button_x, self.challenge_button_y = 0, 200

            # divided into how many rows and cols
            self.rows = 5
            self.cols = 2

            # set up width and height
            self.border_width = 5
            self.cell_dims = (
                self.w / self.cols - self.border_width,
                (self.h - self.challenge_button_y) / self.rows - self.border_width,
            )

            self.on_challenge_button_click = on_challenge_button_click
            self.create_challenge_buttons()

        else:
            self.text = Fonts.user_font.render("This is you!", True, Colors.CYAN)
            self.text_rect = self.text.get_rect(center=(LEFT_WIDTH // 2, 200))
            self.username_input = Text_Input(
                300,
                300,
                400,
                100,
                default_text=self.user["username"],
                callback=lambda text: on_user_name_change({"username": text})
                if len(text) > 0
                else None,
            )

            self.change_user_name_text = Fonts.subtitle_font.render(
                "Change username: ", True, Colors.LIGHT_BLUE
            )
            self.change_user_name_text_rect = self.change_user_name_text.get_rect(
                center=(
                    300 - (Fonts.subtitle_font.size("Change username: ")[0]) / 2 - 10,
                    300 + 50,
                )
            )
            self.image_path_input = Text_Input(
                300,
                500,
                400,
                100,
                default_text="(Right click to paste path)",
                callback=lambda text: on_image_change(text) if len(text) > 0 else None,
            )

            self.change_image_text = Fonts.subtitle_font.render(
                "Change Profile Image: ", True, Colors.LIGHT_BLUE
            )
            self.change_image_text_rect = self.change_image_text.get_rect(
                center=(
                    300
                    - (Fonts.subtitle_font.size("Change Profile Image: ")[0]) / 2
                    - 10,
                    500 + 50,
                )
            )

        self.bg_image = None

    def create_challenge_buttons(self):
        # place the challenge buttons properly
        for ind, game in enumerate(profile_buttons):
            row = ind // self.cols  # related to y-cor
            col = ind % self.cols  # related to x-cor
            self.buttons["buttons"].append(
                ChallengeButton(
                    col * self.cell_dims[0]
                    + self.border_width
                    + self.challenge_button_x,
                    row * self.cell_dims[1]
                    + self.border_width
                    + self.challenge_button_y,
                    self.cell_dims[0] - self.border_width,
                    self.cell_dims[1] - self.border_width,
                    self.user["id"],
                    game,
                    self.on_challenge_button_click,
                )
            )

    def draw(self, win):
        if self.bg_image:
            win.blit(self.bg_image, (0, 0))

        win.blit(self.title, self.title_rect)

        for buttons in self.buttons.values():
            for button in buttons:
                button.show(win)

        if self.text:
            win.blit(self.text, self.text_rect)

        if self.curr_user:
            win.blit(self.change_user_name_text, self.change_user_name_text_rect)
            win.blit(self.change_image_text, self.change_image_text_rect)
            self.username_input.draw(win)
            self.image_path_input.draw(win)

    def disable_challenge_buttons(self):
        for button in self.buttons["buttons"]:
            button.disable()

    def enable_challenge_buttons(self):
        for button in self.buttons["buttons"]:
            button.enable()

    def check_event(self, e):
        for buttons in self.buttons.values():
            for button in buttons:
                button.check_event(e)
        if self.curr_user:
            self.username_input.check_event(e)
            self.image_path_input.check_event(e)

    def check_keys(self, keys):
        if self.curr_user:
            self.username_input.check_keys(keys)
            self.image_path_input.check_keys(keys)

    def update(self, changed):
        if changed.get("username"):
            if self.curr_user:
                self.username_input.update({"default_text": changed["username"]})

            # The title is the username - update it
            self.title = Fonts.user_font.render(changed["username"], True, Colors.WHITE)
            self.title_rect = self.title.get_rect(center=(LEFT_WIDTH // 2, 100))

        if changed.get("image"):
            self.bg_image = pygame.transform.scale(
                changed.get("image"), (int(self.w), int(self.h))
            )
            self.bg_image.set_alpha(50)

    def on_disconnect(self):
        self.text = Fonts.user_font.render("User Disconnected!", True, Colors.CYAN)
        self.text_rect = self.text.get_rect(center=(LEFT_WIDTH // 2, 200))
        self.disable_challenge_buttons()


# the notification base class
class Notification:
    def __init__(
        self,
        title="",
        text="",
        x=0,
        y=HEIGHT - 100,
        w=RIGHT_WIDTH,
        h=95,
        color=Colors.YELLOW,
        mask_color=Colors.ALPHA_BLUE,
        title_color=Colors.BLACK,
        text_color=Colors.BLUE,
        closeable=True,
        on_close=lambda: None,
        button_props=[],
        id=0,
        **kwargs,
    ):
        self.id = id
        self.x, self.y, self.w, self.h = x, y, w, h

        self.color = color
        self.override_color = None

        self.title_font = Fonts.subtitle_font
        self.text_font = Fonts.small_font

        self.surf = pygame.Surface((self.w, self.h))
        self.mask = pygame.Surface((self.w, self.h))
        # self.mask.convert_alpha()
        self.mask_color = mask_color

        title = self.truncate(title, self.title_font)
        self.title = self.title_font.render(title, False, title_color)
        self.title_rect = self.title.get_rect(
            center=(self.w / 2, self.title.get_height() / 2 + 5)
        )
        self.text = None
        if text:
            text = self.truncate(text, self.text_font)
            self.text = self.text_font.render(text, False, text_color)

            self.text_rect = self.text.get_rect(
                center=(
                    self.w / 2,
                    self.text.get_height() / 2 + self.title.get_height() + 10,
                )
            )

        self.on_close = lambda *args, **kwargs: on_close(self.id)
        self.close = Close(self.w - 30, 0, 30, 30, self.on_close)
        self.close.button.real_rect = pygame.Rect(
            self.x + self.w - 30 + LEFT_WIDTH + GAP_BETWEEN_SECTIONS, self.y, 30, 30
        )
        if not closeable:
            self.close.button.disable()
        self.buttons = []
        self.button_props = button_props
        if len(self.button_props):
            self.create_buttons()
            # self.reposition_buttons()

        self.context = kwargs.get("context") if kwargs.get("context") else {}

    def truncate(self, text, font):
        if font.size(text)[0] > self.w:
            while font.size(text + "...")[0] > self.w:
                text = text[:-1]
            text += "..."

        return text

    def create_buttons(self):
        x_start, x_end, y_start, y_end = 0, self.w, 50, self.h - 5
        b_w, b_h = (x_end - x_start) / len(self.button_props), (y_end - y_start)
        for i, props in enumerate(self.button_props):
            b = Button(
                (x_start + i * (b_w), y_start, b_w, b_h),
                props["color"],
                props["func"],
                **props["styles"],
                on_popup_close=self.on_close,
            )
            self.buttons.append(b)

    def move(self, x, y, xoff, yoff):
        self.x, self.y = x, y
        self.move_buttons()
        self.reposition_buttons(xoff, yoff)

    def move_buttons(self):
        for button in self.buttons:
            button.rect = pygame.Rect(
                button.rect.x, button.rect.y, button.rect.width, button.rect.height
            )

    def set_override_color(self, color):
        self.override_color = color

    def remove_override_color(self):
        self.override_color = None

    def reposition_buttons(self, x_off=0, y_off=0):
        for button in self.buttons:
            button.real_rect = pygame.Rect(
                x_off + self.x + button.rect.x,
                y_off + self.y + button.rect.y,
                button.rect.width,
                button.rect.height,
            )
        self.close.button.real_rect = pygame.Rect(
            x_off + self.x + self.close.button.rect.x,
            y_off + self.y + self.close.button.rect.y,
            self.close.button.rect.width,
            self.close.button.rect.height,
        )

    def fade(self):
        if self.mask_color[3] > 0:
            self.mask_color[3] -= 1

    def draw(self, win):
        self.surf.fill(self.override_color or self.color)
        self.surf.blit(self.title, self.title_rect)
        if self.text:
            self.surf.blit(self.text, self.text_rect)
        self.close.show(self.surf)
        for button in self.buttons:
            button.update(self.surf)

        win.blit(self.surf, (self.x, self.y))

    def check_event(self, e):
        self.close.check_event(e)
        for button in self.buttons:
            button.check_event(e, **self.context)


# the cotainer where notifications pop up
class Notification_Container:
    max_messages = 10

    def __init__(self, title, x, y, w=RIGHT_WIDTH, h=340):

        self.x, self.y, self.w, self.h = x, y, w, h

        self.surf = pygame.Surface((self.w, self.h))
        self.title_text = title
        self.title = Fonts.title_font.render(self.title_text, False, Colors.LIGHT_BLUE)
        self.title_rect = self.title.get_rect(center=(self.w // 2, 30))

        self.popups = {}
        self.popups_list = []
        self.neatened_popups = [[]]
        self.current_page = 0
        self.buttons = []
        self.button_height = 50

        self.next = None
        self.prev = None
        self.first = None
        self.create_pagination_buttons()
        self.update_pagination()

        self.page_render = Fonts.notification_font.render(
            f"{self.current_page+1}/{len(self.neatened_popups)}", True, Colors.GRAY
        )
        self.page_render_rect = self.page_render.get_rect(
            center=(
                self.title_rect.x - self.page_render.get_width(),
                self.title_rect.y + self.title_rect.height / 2,
            )
        )

        # popup props
        self.popup_h = 100
        self.popup_gap = 20
        self.popup_w = RIGHT_WIDTH
        self.max_popups = int(
            (self.h - self.button_height - self.title_rect.height) / self.popup_h
        )

        self.num_popups = 0  # this is for popups id
        self.num_noti_center = (
            self.title_rect.x + self.title_rect.width + 30,
            self.title_rect.y + self.title_rect.height / 2,
        )
        self.num_noti = Fonts.notification_font.render(str(0), True, Colors.WHITE)
        self.num_noti_rect = self.num_noti.get_rect(center=self.num_noti_center)

    def prev_page(self, *args, **kwargs):
        self.current_page -= 1 if self.current_page > 0 else 0
        self.update_pagination()

    def next_page(self, *args, **kwargs):
        self.current_page += (
            1 if self.current_page < len(self.neatened_popups) - 1 else 0
        )
        self.update_pagination()

    def first_page(self, *args, **kwargs):
        self.current_page = 0
        self.update_pagination()

    def create_pagination_buttons(self):
        self.next = Button(
            (260, self.h - self.button_height, 50, self.button_height),
            Colors.ORANGE,
            self.next_page,
            image=pygame.transform.scale(Images.next, (50, self.button_height)),
            **Button_Styles.PAGINATION_BUTTON_STYLE,
        )
        self.prev = Button(
            (180, self.h - self.button_height, 50, self.button_height),
            Colors.ORANGE,
            self.prev_page,
            image=pygame.transform.scale(Images.previous, (50, self.button_height)),
            **Button_Styles.PAGINATION_BUTTON_STYLE,
        )
        self.first = Button(
            (100, self.h - self.button_height, 50, self.button_height),
            Colors.ORANGE,
            self.first_page,
            image=pygame.transform.scale(Images.first, (50, self.button_height)),
            **Button_Styles.PAGINATION_BUTTON_STYLE,
        )
        self.buttons.extend([self.next, self.prev, self.first])
        self.reposition_buttons()

    def reposition_buttons(self):
        for button in self.buttons:
            button.real_rect = pygame.Rect(
                self.x + LEFT_WIDTH + GAP_BETWEEN_SECTIONS + button.rect.x,
                self.y + button.rect.y,
                button.rect.width,
                button.rect.height,
            )

    def update_pagination(self):
        self.prev.disable()
        self.first.disable()
        self.next.disable()
        if self.current_page < len(self.neatened_popups) - 1:
            self.next.enable()

        if self.current_page > 0:
            self.prev.enable()
            self.first.enable()
        self.page_render = Fonts.notification_font.render(
            f"{self.current_page+1}/{len(self.neatened_popups)}", True, Colors.GRAY
        )

    def move_popups(self):
        for i, popup in enumerate(self.popups_list):
            x = 0
            y = (
                self.title_rect.height
                + self.popup_gap
                + (i % self.max_popups) * (self.popup_h + self.popup_gap)
            )
            popup.move(x, y, self.x + LEFT_WIDTH + GAP_BETWEEN_SECTIONS, self.y)

    def add_popup(
        self,
        title,
        text="",
        color=Colors.YELLOW,
        title_color=Colors.BLACK,
        text_color=Colors.BLUE,
        closeable=True,
        button_props=[],
        id=None,
        **kwargs,
    ):
        if self.popups.get(id):
            self.popups_list.remove(self.popups.pop(id))

        id = id or self.num_popups
        on_close = lambda *args, **kwargs: self.remove_popup(id)
        x = 0
        w = RIGHT_WIDTH
        h = self.popup_h
        y = (
            self.title_rect.height
            + self.popup_gap
            + (0 % self.max_popups) * (h + self.popup_gap)
        )
        p = Notification(
            title,
            text,
            x=x,
            y=y,
            w=w,
            h=h,
            color=color,
            title_color=title_color,
            text_color=text_color,
            closeable=closeable,
            on_close=on_close,
            button_props=button_props,
            id=id,
            **kwargs,
        )
        p.set_override_color(Colors.CYAN)
        if len(self.popups_list) > 0:
            self.popups_list[0].remove_override_color()
        # p.reposition_buttons(self.x+LEFT_WIDTH+GAP, self.y)
        self.popups[id] = p
        self.popups_list.insert(0, p)
        self.num_popups += 1

        if len(self.popups_list) > self.max_messages:
            self.remove_popup(self.popups_list[-1].id)

        self.update_noti()
        self.move_popups()

        self.neaten_popups()
        self.update_pagination()

    def update_noti(self):
        self.num_noti = Fonts.notification_font.render(
            str(len(self.popups)), False, Colors.WHITE
        )
        self.num_noti_rect = self.num_noti.get_rect(center=self.num_noti_center)

    def remove_popup(self, id):
        ind = self.popups_list.index(self.popups.pop(id))
        self.popups_list.pop(ind)
        self.update_noti()
        self.move_popups()

        self.neaten_popups()
        self.update_pagination()

    def neaten_popups(self):
        self.neatened_popups = []
        r = -1
        for c, popup in enumerate(self.popups_list):
            if c % self.max_popups == 0:
                self.neatened_popups.append([])
                r += 1
            self.neatened_popups[r].append(popup)

        if len(self.neatened_popups) - 1 < self.current_page:
            self.current_page = (
                len(self.neatened_popups) - 1 if len(self.neatened_popups) > 0 else 0
            )
        if len(self.neatened_popups) == 0:
            self.neatened_popups.append([])

    def draw(self, win):
        self.surf.fill(Colors.BG_COLOR)
        if len(self.neatened_popups) > 0:
            for popup in self.neatened_popups[self.current_page]:
                popup.draw(self.surf)

        for button in self.buttons:
            button.update(self.surf)

        self.surf.blit(self.title, self.title_rect)

        if len(self.popups) > 0:
            pygame.draw.circle(
                self.surf, Colors.RED, self.num_noti_center, 15,
            )
            self.surf.blit(self.num_noti, self.num_noti_rect)
        self.surf.blit(self.page_render, self.page_render_rect)

        win.blit(self.surf, (self.x, self.y))

    def check_event(self, e):
        if len(self.neatened_popups) > 0:
            for popup in self.neatened_popups[self.current_page]:
                popup.check_event(e)
        for button in self.buttons:
            button.check_event(e)


# the tic tac toe board
class TTT_Board:
    def __init__(
        self,
        X_id,
        O_id,
        x=0,
        y=110,
        w=LEFT_WIDTH - 100,
        h=HEIGHT - 100,
        rows=3,
        cols=3,
        on_button_click=lambda *args, **kwargs: None,
    ):
        self.X_id, self.O_id = X_id, O_id

        self.x, self.y, self.w, self.h = x, y, w, h
        self.surf = pygame.Surface((self.w, self.h))
        self.rows, self.cols = rows, cols

        self.border_width = 3

        # calculate correct sizes of border_width, button_width and button_height
        self.b_w = (self.w - ((self.cols + 2) * self.border_width)) / self.cols
        self.b_h = (self.h - ((self.rows + 2) * self.border_width)) / self.rows

        self.board = []
        self.on_button_click = on_button_click
        self.generate_board()
        self.reposition_buttons()

    def generate_board(self):
        for ind in range(self.rows * self.cols):
            row = ind // self.cols  # related to y-cor
            col = ind % self.cols  # related to x-cor
            self.board.append(
                Button(
                    (
                        col * (self.b_w + self.border_width) + self.border_width,
                        row * (self.b_h + self.border_width) + self.border_width,
                        self.b_w,
                        self.b_h,
                    ),
                    Colors.WHITE,
                    function=self.on_button_click,
                    id=ind,
                    **Button_Styles.TTT_BUTTON_STYLE,
                )
            )

    def reposition_buttons(self):
        for button in self.board:
            button.real_rect = pygame.Rect(
                self.x + button.rect.x,
                self.y + button.rect.y,
                button.rect.width,
                button.rect.height,
            )

    def disable_all(self):
        for button in self.board:
            button.disable()

    def place(self, id, text):
        self.board[id].change_text(text)
        self.board[id].disable()

    def draw(self, win):
        self.surf.fill(Colors.BLUE)
        for b in self.board:
            b.update(self.surf)

        win.blit(self.surf, (self.x, self.y))

    def check_event(self, e):
        for button in self.board:
            button.check_event(e)

    def game_over_protocol(self, indices, *args):
        if indices:
            for index in indices:
                self.board[index].set_highlight(Colors.GREEN)

        self.disable_all()


# the connect4 board
class Connect4_Board:
    padding = 10  # pad everything, so that it looks neater

    def __init__(
        self,
        curr_player_id,
        red_id,
        blue_id,
        x=0,
        y=110,
        w=LEFT_WIDTH - 70,
        h=HEIGHT - 110,
        rows=12,
        cols=13,
        on_button_click=lambda *args, **kwargs: None,
        **kwargs,
    ):

        self.red_id, self.blue_id = red_id, blue_id
        self.player_color = "red" if self.red_id == curr_player_id else "blue"

        self.x, self.y, self.w, self.h = (
            x,
            y,
            w,
            h,
        )
        self.surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.rows, self.cols = rows, cols

        self.border_width = 3

        # calculate correct size of cell_width and cell_height
        self.cell_w = (self.w - 2 * self.padding - self.border_width) / (
            self.cols
        ) - self.border_width
        self.cell_h = (self.h - 2 * self.padding - self.border_width) / (
            self.rows + 1
        ) - self.border_width  # adjust for the top row
        self.cell_d = int(min(self.cell_w, self.cell_h))  # diameter

        # load images
        self.red_coin_image = pygame.transform.scale(
            Images.red_coin, (self.cell_d, self.cell_d)
        ).convert_alpha()

        self.blue_coin_image = pygame.transform.scale(
            Images.blue_coin, (self.cell_d, self.cell_d),
        ).convert_alpha()

        self.coin_image = (
            self.red_coin_image if self.player_color == "red" else self.blue_coin_image
        )

        # the board - None is open, red is filled with red coin, and blue is filled with blue coin
        self.board = [[None for c in range(self.cols)] for r in range(self.rows)]

        self.on_button_click = on_button_click

        # the top *holes* row - through which user can insert a coin
        self.top_bar_height = self.cell_h
        self.top_bar_buttons = self.create_buttons()
        self.reposition_buttons()

        # variable to control the animating coin, when some one wins
        self.game_over = False
        self.winning_indices = []
        self.coin_brigthness = 0
        self.change_brightness_by = 5
        self.winning_coin = None

    # create the top row buttons
    def create_buttons(self):
        buttons = [
            Button(
                (
                    self.border_width
                    + self.padding
                    + col * (self.cell_w + self.border_width),
                    self.border_width + self.padding + self.border_width,
                    self.cell_w,
                    self.cell_h,
                ),
                Colors.LIGHT_BLUE,
                function=self.on_button_click,
                id=col,
                **Button_Styles.CONNECT4_BUTTON_STYLE,
                hover_image=self.coin_image,
            )
            for col in range(self.cols)
        ]
        return buttons

    # get the co-ordinates, provided the row and column
    def get_coords(self, row, col, buffer_height=0, center=False):
        if center:
            return (
                self.border_width
                + self.padding
                + col * (self.border_width + self.cell_w)
                + self.cell_w / 2,
                self.border_width
                + self.padding
                + row * (self.border_width + self.cell_h)
                + self.cell_h / 2
                + buffer_height,
            )
        return (
            self.border_width + self.padding + col * (self.border_width + self.cell_w),
            self.border_width
            + self.padding
            + row * (self.border_width + self.cell_h)
            + buffer_height,
        )

    # button events require "correct" co ordinates, where as displaying the button requires relativ co-ords
    def reposition_buttons(self):
        for button in self.top_bar_buttons:
            button.real_rect = pygame.Rect(
                self.x + button.rect.x,
                self.y + button.rect.y,
                button.rect.width,
                button.rect.height,
            )

    # draw the board
    def draw(self, win):

        if self.game_over and len(self.winning_indices) > 0:
            # make some nice animating coins, when some on wins
            self.winning_coin.set_alpha(self.coin_brigthness)

            for row, col in self.winning_indices:
                pygame.draw.circle(
                    self.surf,
                    Colors.WHITE,
                    self.get_coords(
                        row, col, buffer_height=self.top_bar_height, center=True
                    ),
                    self.cell_d / 2,
                )

                self.surf.blit(
                    self.winning_coin,
                    self.get_coords(row, col, buffer_height=self.top_bar_height),
                )

                pygame.draw.circle(
                    self.surf,
                    Colors.BROWN,
                    self.get_coords(
                        row, col, buffer_height=self.top_bar_height, center=True
                    ),
                    self.cell_d / 2,
                    width=3,
                )

            if self.coin_brigthness >= 255:
                self.change_brightness_by = -5
            elif self.coin_brigthness <= 0:
                self.change_brightness_by = 5

            self.coin_brigthness += self.change_brightness_by

        else:
            # draw the board
            self.surf.fill(Colors.LIGHT_BROWN)

            for row in range(self.rows):
                for col in range(self.cols):
                    cell = self.board[row][col]

                    if cell == "red":
                        self.surf.blit(
                            self.red_coin_image,
                            self.get_coords(
                                row, col, buffer_height=self.top_bar_height
                            ),
                        )

                    elif cell == "blue":
                        self.surf.blit(
                            self.blue_coin_image,
                            self.get_coords(
                                row, col, buffer_height=self.top_bar_height
                            ),
                        )

                    else:
                        pygame.draw.circle(
                            self.surf,
                            Colors.WHITE,
                            self.get_coords(
                                row, col, buffer_height=self.top_bar_height, center=True
                            ),
                            self.cell_d / 2,
                        )

                    pygame.draw.circle(
                        self.surf,
                        Colors.BROWN,
                        self.get_coords(
                            row, col, buffer_height=self.top_bar_height, center=True
                        ),
                        self.cell_d / 2,
                        width=3,
                    )

            for button in self.top_bar_buttons:
                button.update(self.surf)

            pygame.draw.rect(
                self.surf, Colors.BROWN, (0, 0, self.w, self.h), self.padding
            )

        win.blit(self.surf, (self.x, self.y))

    # check for top row button events
    def check_event(self, e):
        for button in self.top_bar_buttons:
            button.check_event(e)

    # what happens when the game ends?
    def game_over_protocol(self, indices, winner_id, *args):
        # disable all buttons
        for button in self.top_bar_buttons:
            button.hover_image = None
            button.disable()
            button.update(self.surf)

        # setup animation vars
        self.game_over = True
        self.winning_coin = (
            self.red_coin_image if self.red_id == winner_id else self.blue_coin_image
        ).copy()
        self.winning_indices = indices or []

    # place a coin in the desired location
    def place(self, to, turn_string):
        self.board[to[0]][to[1]] = turn_string
        if to[0] == 0:
            self.top_bar_buttons[to[1]].hover_image = None
            self.top_bar_buttons[to[1]].disable()
            self.top_bar_buttons[to[1]].update(self.surf)


# base game board, for all games... if more
class Game_Template:
    def __init__(
        self,
        curr_user_id,
        players,
        players_identification_text,
        turn_id,
        game,
        board,
        on_quit,
    ):
        self.curr_user_id = curr_user_id
        self.turn_id = turn_id

        self.players = players
        self.game = game
        self.board = board

        self.w, self.h = LEFT_WIDTH, HEIGHT
        self.surf = pygame.Surface((self.w, self.h))

        self.quit_button = Button(
            (LEFT_WIDTH - 50, HEIGHT // 2, 50, 50),
            Colors.RED,
            on_quit,
            text="X",
            truncate=False,
            **Button_Styles.QUIT_BUTTON_STYLE,
        )

        self.title_text = ""
        for ind, id in enumerate(self.players.keys()):
            self.title_text += f"{self.players[id]['username'][:3]+'...' if len(self.players[id]['username'])>5 else self.players[id]['username']} {'[you]' if self.curr_user_id==id else ''} ( {players_identification_text[id]} )"
            self.title_text += " vs. " if ind < len(self.players) - 1 else ""

        self.title = Fonts.title_font.render(self.title_text, True, Colors.WHITE)
        self.title_rect = self.title.get_rect(center=(self.w // 2, 50))
        self.text = None
        self.set_turn(self.turn_id)
        self.text_rect = self.text.get_rect(center=(self.w // 2, 95))

        self.game_over = False

        self.show_animated_bg = False

    def draw(self, win):
        self.surf.fill(Colors.BG_COLOR)

        if self.show_animated_bg:
            self.bg.play(self.surf)
            self.bg_close_button.show(self.surf)

        else:
            self.quit_button.update(self.surf)
            self.surf.blit(self.title, self.title_rect)
            self.surf.blit(self.text, self.text_rect)
            self.board.draw(self.surf)

        win.blit(self.surf, (0, 0))

    def set_turn(self, turn_id):
        self.turn_id = turn_id
        if self.turn_id == self.curr_user_id:
            self.text = Fonts.subtitle_font.render(
                "You are up!", True, Colors.LIGHT_BLUE
            )

        else:
            turn_username = (
                self.players[turn_id]["username"][:3] + "..."
                if len(self.players[turn_id]["username"]) > 5
                else self.players[turn_id]["username"]
            )
            self.text = Fonts.subtitle_font.render(
                f"{turn_username}'s turn!", True, Colors.LIGHT_BLUE
            )

    def game_over_protocol(self, game_over_detials):
        winner_id = game_over_detials.get("winner_id")
        indices = game_over_detials.get("indices")

        self.board.game_over_protocol(indices, winner_id)

        if not winner_id or game_over_detials.get("tie"):
            text = "Tie Match!"
        elif winner_id == self.curr_user_id:
            text = "You have won!"

            def on_bg_close(*args, **kwargs):
                self.show_animated_bg = False
                Sound_Effects.celebration.stop()
                if saved_settings["play_music"]:
                    pygame.mixer.music.unpause()

            self.bg_close_button = Close(self.w - 60, 60, on_click=on_bg_close)
            self.bg = random.choice(celebrations)(self.w, self.h, 0, 0, text=text)

            self.show_animated_bg = True

            pygame.mixer.music.pause()
            if saved_settings["sound_effects"]:
                Sound_Effects.celebration.play()

        else:
            text = f"{(self.players[winner_id]['username'][:3]+'...')if len(self.players[winner_id]['username'])>5 else self.players[winner_id]['username']} has won!"

            def on_bg_close(*args, **kwargs):
                self.show_animated_bg = False
                Sound_Effects.mourn.stop()
                if saved_settings["play_music"]:
                    pygame.mixer.music.unpause()

            self.bg_close_button = Close(self.w - 60, 60, on_click=on_bg_close)
            self.bg = random.choice(mourns)(self.w, self.h, 0, 0, text="You have Lost!")

            self.show_animated_bg = True

            pygame.mixer.music.pause()
            if saved_settings["sound_effects"]:
                Sound_Effects.mourn.play()

        self.text = Fonts.subtitle_font.render(text, True, Colors.GREEN)
        self.game_over = True

    def check_event(self, e):
        self.quit_button.check_event(e)

        if not self.game_over:

            self.board.check_event(e)

        if self.show_animated_bg:
            self.bg_close_button.check_event(e)


# previous, next and home buttons
class Navigators:
    def __init__(self, on_prev_click, on_next_click, on_home_click, on_settings_click):
        self.gap = 20  # 20 gap between two buttons
        self.h = 90
        self.x = 0
        self.y = 0
        self.button_w = RIGHT_WIDTH // 4
        self.surf = pygame.Surface((RIGHT_WIDTH, self.h))
        self.buttons = [
            Button(
                (0, 10, self.button_w, 80),
                Colors.RED,
                on_prev_click,
                border_radius=50,
                image=pygame.transform.scale(Images.previous, (self.button_w, 80)),
                **Button_Styles.NAVIGATION_BUTTON_STYLE,
            ),
            Button(
                (self.button_w, 10, self.button_w, 80,),
                Colors.BLUE,
                on_next_click,
                border_radius=50,
                image=pygame.transform.scale(Images.next, (self.button_w, 80)),
                **Button_Styles.NAVIGATION_BUTTON_STYLE,
            ),
            Button(
                ((self.button_w) * 2, 10, self.button_w, 80,),
                Colors.WHITE,
                on_home_click,
                image=pygame.transform.scale(
                    Images.home, (min(self.button_w, 80), min(self.button_w, 80))
                ),
                **Button_Styles.NAVIGATION_BUTTON_STYLE,
            ),
            Button(
                ((self.button_w) * 3, 10, self.button_w, 80,),
                Colors.WHITE,
                on_settings_click,
                image=pygame.transform.scale(
                    Images.settings, (min(self.button_w, 80), min(self.button_w, 80))
                ),
                **Button_Styles.NAVIGATION_BUTTON_STYLE,
            ),
        ]
        self.reposition_buttons()

    def update_buttons(self, current_page, displays):
        for button in self.buttons:
            button.disable()

        if current_page > 0:
            self.buttons[0].enable()
        if current_page < len(displays) - 1:
            self.buttons[1].enable()
        if displays[current_page] != "home":
            self.buttons[2].enable()

        if displays[current_page] != "settings":
            self.buttons[3].enable()

    def draw(self, win):
        for button in self.buttons:
            button.update(self.surf)
        win.blit(self.surf, (self.x, self.y))

    def reposition_buttons(self, x_off=LEFT_WIDTH + GAP_BETWEEN_SECTIONS, y_off=0):
        for button in self.buttons:
            button.real_rect = pygame.Rect(
                x_off + self.x + button.rect.x,
                y_off + self.y + button.rect.y,
                button.rect.width,
                button.rect.height,
            )

    def check_event(self, e, current_page, display):
        self.update_buttons(current_page, display)
        for button in self.buttons:
            button.check_event(e)


class Text_Input:
    def __init__(
        self,
        x,
        y,
        w,
        h,
        x_off=0,
        y_off=0,
        default_text="write",
        font=Fonts.subtitle_font,
        font_color=Colors.BLACK,
        bg_color=Colors.WHITE,
        hover_color=Colors.GRAY,
        number=False,
        callback=None,
    ):
        self.x, self.y = x, y
        self.real_x, self.real_y = self.x + x_off, self.y + y_off
        self.w, self.h = w, h

        self.surf = pygame.Surface((w, h))

        self.rect = self.surf.get_rect(topleft=(self.real_x, self.real_y))

        self.default_text = default_text
        self.text = ""
        self.font = font
        self.font_color = font_color
        self.bg_color = bg_color
        self.hover_color = hover_color

        self.hovered = False
        self.selected = False

        self.number = number
        self.callback = callback

        self.clear_button = Close(
            self.w - 20, 0, 20, 20, lambda *args, **kwargs: self.clear()
        )
        self.clear_button.button.real_rect = pygame.Rect(
            self.real_x + self.w - 20, self.real_y + 0, 20, 20
        )

    def get_text(self):
        return self.text

    def clear(self):
        self.text = ""

    def check_keys(self, keys):
        if keys[pygame.K_DELETE] or keys[pygame.K_BACKSPACE]:
            if len(self.text) > 0:
                self.text = self.text[:-1]
                if saved_settings["sound_effects"]:
                    Sound_Effects.key_delete.stop()
                    Sound_Effects.key_delete.play()

    def check_event(self, e):

        self.check_hover()
        self.clear_button.check_event(e)

        if e.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(e.pos):
                if not self.selected and saved_settings["sound_effects"]:
                    Sound_Effects.select.play()
                self.selected = True

            elif self.selected:
                self.selected = False
            # 3 is right click
            if e.button == 3 and self.selected:
                self.text += pyperclip.paste()
                if saved_settings["sound_effects"]:
                    Sound_Effects.key_add.stop()
                    Sound_Effects.key_add.play()

        if e.type == pygame.KEYDOWN and self.selected:

            # callback on enter
            if e.key == pygame.K_RETURN and self.callback is not None:
                self.selected = False
                self.callback(self.text)
                if saved_settings["sound_effects"]:
                    Sound_Effects.key_add.stop()
                    Sound_Effects.key_add.play()

            # paste
            elif e.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self.text += pyperclip.paste()
                if saved_settings["sound_effects"]:
                    Sound_Effects.key_add.stop()
                    Sound_Effects.key_add.play()

            # write
            else:
                if self.number:
                    if str(e.unicode).isdigit():
                        self.text += e.unicode
                        if saved_settings["sound_effects"]:
                            Sound_Effects.key_add.stop()
                            Sound_Effects.key_add.play()

                else:
                    self.text += e.unicode
                    if saved_settings["sound_effects"]:
                        Sound_Effects.key_add.stop()
                        Sound_Effects.key_add.play()

    def check_hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and not self.selected:
            self.hovered = True
        elif self.hovered:
            self.hovered = False

    def draw(self, win):
        self.surf.fill(self.bg_color)

        if self.selected:
            pygame.draw.rect(self.surf, Colors.GREEN, (0, 0, self.w, self.h), 5)
        elif self.hovered:
            self.surf.fill(self.hover_color)

        if len(self.text) > 0:
            text_render = self.font.render(self.text, False, self.font_color)
            text_rect = text_render.get_rect(center=(self.w / 2, (self.h) / 2))
            self.surf.blit(text_render, text_rect)

        elif len(self.default_text) > 0:
            text_render = self.font.render(self.default_text, False, Colors.GRAY)
            text_rect = text_render.get_rect(center=(self.w / 2, (self.h) / 2))
            self.surf.blit(text_render, text_rect)

        self.clear_button.show(self.surf)

        win.blit(self.surf, (self.x, self.y))

    def update(self, changed):
        self.__dict__.update(changed)


class Settings_Page:
    def __init__(
        self, on_close, x=0, y=0, w=LEFT_WIDTH, h=HEIGHT,
    ):
        self.x, self.y, self.w, self.h = x, y, int(w), int(h)
        self.surf = pygame.Surface((self.w, self.h))

        # The title
        self.title = Fonts.title_font.render("Settings", True, Colors.WHITE)
        self.title_rect = self.title.get_rect(center=(self.w // 2, 100))

        self.mute_music_button = Button(
            (self.w / 2 + 100, 200, 50, 50,),
            Colors.BLUE,
            self.mute_music,
            **Button_Styles.CONNECT4_BUTTON_STYLE,
            image=pygame.transform.scale(Images.unmuted, (50, 50)),
        )
        self.mute_sound_effects_button = Button(
            (self.w / 2 + 100, 300, 50, 50,),
            Colors.BLUE,
            self.mute_sound_effects,
            **Button_Styles.CONNECT4_BUTTON_STYLE,
            image=pygame.transform.scale(Images.unmuted, (50, 50)),
        )
        self.buttons = {
            "close": Close(self.w - 80, 80, 50, 50, on_close),
            "mute_music": self.mute_music_button,
            "mute_sound_effects": self.mute_sound_effects_button,
        }

        self.update_mute_music_button()
        self.update_mute_sound_effects_button()
        self.render_text()

    def render_text(self):
        self.surf.blit(self.title, self.title_rect)
        self.surf.blit(self.mute_music_text, self.mute_music_text_rect)
        self.surf.blit(self.mute_sound_effect_text, self.mute_sound_effect_text_rect)

    def update_saved_settings(self):
        with open("saved_settings.json", "w") as f:
            json.dump(saved_settings, f)

    def update_mute_music_button(self):
        if saved_settings["play_music"]:
            self.mute_music_button.function = self.mute_music
            self.mute_music_button.color = Colors.BLUE
            self.mute_music_button.image = pygame.transform.scale(
                Images.unmuted, (50, 50)
            )

            self.mute_music_text = Fonts.subtitle_font.render(
                "Mute Music: ", True, Colors.LIGHT_BLUE
            )
            self.mute_music_text_rect = self.mute_music_text.get_rect(
                center=(self.w / 2 - 50, 225)
            )
        else:
            self.mute_music_button.function = self.unmute_music
            self.mute_music_button.color = Colors.RED
            self.mute_music_button.image = pygame.transform.scale(
                Images.muted, (50, 50)
            )

            self.mute_music_text = Fonts.subtitle_font.render(
                "Unmute Music: ", True, Colors.LIGHT_BLUE
            )
            self.mute_music_text_rect = self.mute_music_text.get_rect(
                center=(self.w / 2 - 50, 225)
            )

    def update_mute_sound_effects_button(self):
        if saved_settings["sound_effects"]:
            self.mute_sound_effects_button.function = self.mute_sound_effects
            self.mute_sound_effects_button.color = Colors.BLUE
            self.mute_sound_effects_button.image = pygame.transform.scale(
                Images.unmuted, (50, 50)
            )

            self.mute_sound_effect_text = Fonts.subtitle_font.render(
                "Mute Sound Effects: ", True, Colors.LIGHT_BLUE
            )
            self.mute_sound_effect_text_rect = self.mute_sound_effect_text.get_rect(
                center=(self.w / 2 - 50, 325)
            )
        else:
            self.mute_sound_effects_button.function = self.unmute_sound_effects
            self.mute_sound_effects_button.color = Colors.RED
            self.mute_sound_effects_button.image = pygame.transform.scale(
                Images.muted, (50, 50)
            )

            self.mute_sound_effect_text = Fonts.subtitle_font.render(
                "Unmute Sound Effects: ", True, Colors.LIGHT_BLUE
            )
            self.mute_sound_effect_text_rect = self.mute_sound_effect_text.get_rect(
                center=(self.w / 2 - 50, 325)
            )

    def mute_music(self, *args, **kwargs):
        saved_settings["play_music"] = False
        self.update_saved_settings()
        mixer.music.stop()
        self.update_mute_music_button()

    def unmute_music(self, *args, **kwargs):
        saved_settings["play_music"] = True
        self.update_saved_settings()
        mixer.music.play(-1)

        self.update_mute_music_button()

    def mute_sound_effects(self, *args, **kwargs):
        saved_settings["sound_effects"] = False
        self.update_saved_settings()
        self.update_mute_sound_effects_button()

    def unmute_sound_effects(self, *args, **kwargs):
        saved_settings["sound_effects"] = True
        self.update_saved_settings()
        self.update_mute_sound_effects_button()

    def check_event(self, e):
        for button in self.buttons.values():
            button.check_event(e)

    def draw(self, win):
        self.surf.fill(Colors.BG_COLOR)
        self.render_text()
        for button in self.buttons.values():
            button.update(self.surf)

        win.blit(self.surf, (self.x, self.y))
