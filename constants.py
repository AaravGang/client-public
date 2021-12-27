import pygame, json
from pygame import mixer

pygame.font.init()
pygame.mixer.init()


# window settings
with open("saved_settings.json", "r") as f:
    saved_settings = json.load(f)

# All colors
class Colors:
    BG_COLOR = (34, 34, 34)
    RED = (250, 0, 0)
    GREEN = (25, 250, 10)
    BLUE = (25, 25, 255)
    ALPHA_BLUE = [255, 0, 255, 150]
    PINK = (250, 10, 150)
    YELLOW = (255, 255, 0)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    CYAN = (0, 255, 255)
    LIGHT_BROWN = (205, 144, 96)
    LIGHT_BLUE = (159, 208, 220)
    ORANGE = (206, 11, 43)
    GRAY = (128, 128, 128)
    TRANSPARENT = (0, 0, 0, 0)
    BROWN = (153, 107, 63)
    PURPLE = (230, 230, 250)
    USER_COLORS = [PINK, ORANGE, BLUE, GREEN, RED]


# bg music
bg_music_path = "static/sounds/background_music.mp3"
pygame.mixer.music.load(bg_music_path)

# sounds
class Sound_Effects:
    default_sounds_path = "static/sounds"

    click = mixer.Sound(f"{default_sounds_path}/click_mouse.ogg")
    select = mixer.Sound(f"{default_sounds_path}/Ping.wav")
    message = mixer.Sound(f"{default_sounds_path}/event.ogg")
    error = mixer.Sound(f"{default_sounds_path}/error.wav")
    key_delete = mixer.Sound(f"{default_sounds_path}/key_delete.ogg")
    key_add = mixer.Sound(f"{default_sounds_path}/key_add.ogg")
    cancel = mixer.Sound(f"{default_sounds_path}/cancel.wav")
    close = cancel
    game_start = mixer.Sound(f"{default_sounds_path}/game_start.wav")
    open = mixer.Sound(f"{default_sounds_path}/open_menu.ogg")
    celebration = mixer.Sound(f"{default_sounds_path}/celebration.wav")
    mourn = mixer.Sound(f"{default_sounds_path}/mourn.wav")


# load images
class Images:
    default_images_path = "static/images"

    muted = pygame.image.load(f"{default_images_path}/muted.png")
    unmuted = pygame.image.load(f"{default_images_path}/unmuted.png")
    sad_images = [pygame.image.load(f"static/images/sad-{i}.png") for i in range(1, 5)]
    settings = pygame.image.load(f"{default_images_path}/settings.png")
    home = pygame.image.load(f"{default_images_path}/home.png")
    next = pygame.image.load(f"{default_images_path}/next.png")
    previous = pygame.image.load(f"{default_images_path}/previous.png")
    first = pygame.image.load(f"{default_images_path}/first.png")
    red_coin = pygame.image.load(f"{default_images_path}/red_coin.png")
    blue_coin = pygame.image.load(f"{default_images_path}/blue_coin.png")


# the two main windows stuff...
HEIGHT = 800
GAP_BETWEEN_SECTIONS = 20
LEFT_WIDTH = 800 - GAP_BETWEEN_SECTIONS
RIGHT_WIDTH = 400
WIDTH = LEFT_WIDTH + RIGHT_WIDTH + GAP_BETWEEN_SECTIONS

# profile pic image dimensions
img_w, img_h = 256, 256


# What all buttons will be displayed on the profile
profile_buttons = ["tic_tac_toe", "connect4"]


# All the fonts
class Fonts:
    default_font_path = "static/fonts"
    user_font = pygame.font.Font(f"{default_font_path}/Chalkduster.ttf", 50,)

    close_button_font = pygame.font.Font(f"{default_font_path}/Arial.ttf", 50,)
    # close_button_font.set_bold(True)

    challenge_button_font = pygame.font.Font(f"{default_font_path}/MarkerFelt.ttc", 30)
    title_font = pygame.font.Font(f"{default_font_path}/ComicSansMSBold.ttf", 30,)
    subtitle_font = pygame.font.Font(f"{default_font_path}/TimesNewRomanBold.ttf", 25,)
    notification_font = pygame.font.Font(f"{default_font_path}/Arial.ttf", 20,)
    small_font = pygame.font.Font(f"{default_font_path}/Arial.ttf", 15)


# All the button styles
class Button_Styles:
    QUIT_BUTTON_STYLE = {
        "font": Fonts.close_button_font,
        "font_color": Colors.BLACK,
        "hover_color": Colors.LIGHT_BLUE,
        "clicked_color": Colors.CYAN,
        "clicked_font_color": Colors.LIGHT_BROWN,
        "hover_font_color": Colors.ORANGE,
        "click_sound": Sound_Effects.close,
    }
    NAVIGATION_BUTTON_STYLE = {
        "font": Fonts.close_button_font,
        "font_color": Colors.BLACK,
        "hover_color": Colors.LIGHT_BLUE,
        "clicked_color": Colors.CYAN,
        "clicked_font_color": Colors.LIGHT_BROWN,
        "hover_font_color": Colors.ORANGE,
        "click_sound": Sound_Effects.click,
    }

    TTT_BUTTON_STYLE = {
        "font": Fonts.close_button_font,
        "font_color": Colors.BLACK,
        "hover_color": Colors.LIGHT_BLUE,
        "clicked_color": Colors.CYAN,
        "clicked_font_color": Colors.LIGHT_BROWN,
        "hover_font_color": Colors.ORANGE,
    }

    USER_BUTTON_STYLE = {
        "font": Fonts.user_font,
        "hover_color": Colors.LIGHT_BLUE,
        "clicked_color": Colors.CYAN,
        "clicked_font_color": Colors.LIGHT_BROWN,
        "hover_font_color": Colors.ORANGE,
        "click_sound": Sound_Effects.open,
    }

    PAGINATION_BUTTON_STYLE = {
        "font": Fonts.subtitle_font,
        "font_color": Colors.WHITE,
        "hover_color": Colors.LIGHT_BLUE,
        "clicked_color": Colors.CYAN,
        "clicked_font_color": Colors.LIGHT_BROWN,
        "hover_font_color": Colors.ORANGE,
        "click_sound": Sound_Effects.click,
        "border_radius": 50,
    }

    CLOSE_BUTTON_STYLE = {
        "font_color": Colors.BLACK,
        "hover_color": Colors.LIGHT_BROWN,
        "clicked_color": Colors.CYAN,
        "clicked_font_color": Colors.BLUE,
        "hover_font_color": Colors.ORANGE,
        "border_radius": 20,
        "click_sound": Sound_Effects.close,
    }

    CHALLENGE_BUTTON_STYLE = {
        "font": Fonts.challenge_button_font,
        "font_color": Colors.BLACK,
        "hover_color": Colors.LIGHT_BLUE,
        "clicked_color": Colors.CYAN,
        "clicked_font_color": Colors.LIGHT_BROWN,
        "hover_font_color": Colors.ORANGE,
    }

    # challenge popup button styles
    CANCEL_BUTTON_STYLE = {
        "font_color": Colors.BLACK,
        "hover_color": Colors.LIGHT_BROWN,
        "clicked_color": Colors.CYAN,
        "clicked_font_color": Colors.BLUE,
        "hover_font_color": Colors.ORANGE,
        "border_radius": 5,
        "text": "Cancel",
    }

    ACCEPT_BUTTON_STYLE = {
        "font_color": Colors.BLACK,
        "hover_color": Colors.LIGHT_BROWN,
        "clicked_color": Colors.CYAN,
        "clicked_font_color": Colors.BLUE,
        "hover_font_color": Colors.ORANGE,
        "border_radius": 5,
        "text": "Accept",
    }
    REJECT_BUTTON_STYLE = {
        "font_color": Colors.BLACK,
        "hover_color": Colors.LIGHT_BROWN,
        "clicked_color": Colors.CYAN,
        "clicked_font_color": Colors.BLUE,
        "hover_font_color": Colors.ORANGE,
        "border_radius": 5,
        "text": "Reject",
        "click_sound": Sound_Effects.cancel,
    }

    CONNECT4_BUTTON_STYLE = {
        "hover_color": Colors.GRAY,
        "clicked_color": Colors.CYAN,
        "border_radius": 50,
    }

    RADIO_BUTTON_STYLE = {
        "hover_color": Colors.GRAY,
        "border_radius": 50,
        "click_sound": Sound_Effects.click,
    }

