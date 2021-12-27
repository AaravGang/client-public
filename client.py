import pygame, json, time, pickle
from pygame import mixer
import numpy as np
from network import Network
from constants import *
from utilities import *
from _thread import start_new_thread

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
# two parts of the window - left and right
WINDOW_LEFT = pygame.Surface((LEFT_WIDTH, HEIGHT))
# right is reserved for messages and errors
WINDOW_RIGHT = pygame.Surface((RIGHT_WIDTH, HEIGHT))


clock = pygame.time.Clock()
fps = 30
run = True


# write something on the screen
def write(win, string, x, y, font=Fonts.title_font, color=Colors.LIGHT_BLUE):
    text = font.render(string, False, color)
    text_rect = text.get_rect(center=(x, y))
    win.blit(text, text_rect)
    pygame.display.update()


# UI to connect
def start_up_window():
    server_ip_input = Text_Input(50, 200, WIDTH / 2 - 100, 100, default_text="Enter IP")
    server_port_input = Text_Input(
        WIDTH / 2 + 50,
        200,
        WIDTH / 2 - 100,
        100,
        default_text="Enter Port (Number only)",
        number=True,
    )
    details = None

    def on_click(*args, **kwargs):
        return server_ip_input.get_text(), server_port_input.get_text()

    connect_button = Button(
        (WIDTH / 2 - 100, HEIGHT / 2 + 100, 200, 100),
        Colors.GREEN,
        on_click,
        text="connect",
        **Button_Styles.CHALLENGE_BUTTON_STYLE,
    )
    while not details:
        clock.tick(fps)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            server_ip_input.check_event(e)
            server_port_input.check_event(e)
            details = connect_button.check_event(e)

        keys = pygame.key.get_pressed()
        server_ip_input.check_keys(keys)
        server_port_input.check_keys(keys)

        server_ip_input.draw(WINDOW)
        server_port_input.draw(WINDOW)
        connect_button.update(WINDOW)
        pygame.display.update()
    return details


# connect to the server
def connect(error=None):
    WINDOW.fill(Colors.BLACK)
    pygame.display.update()
    if error:
        write(WINDOW, error, WIDTH / 2, 100, color=Colors.RED)
    else:
        write(WINDOW, "Enter IP and port to connect to.", WIDTH / 2, 100)

    ip, port = start_up_window()
    if not str(port).isnumeric():
        WINDOW.fill(Colors.BLACK)
        return connect(error="Port must be a valid number.")
    n = Network(ip, int(port))  # initialise a network
    data = n.connect()  # connect to the server
    if data:
        curr_user_id = data
        return n, curr_user_id
    else:
        WINDOW.fill(Colors.BLACK)
        return connect(
            error="Could not connect. Please check if the IP and Port are correct."
        )


# recieve the list of active users from the server
def recieve_active_users():
    WINDOW.fill(Colors.BLACK)
    write(WINDOW, f"Recieving other users from server. - {0}%", WIDTH / 2, HEIGHT / 2)

    try:
        data = n.recv()
        size = data["active_users"][
            "size"
        ]  # recieve the number of bytes the server is gonna send
        full_bytes = b""

        bytes_chunck = ""  # image will come in as bytes
        server_down = False
        while len(full_bytes) != size:
            if len(full_bytes) > size:
                raise Exception("SOMETHING WENT WRONG!")

            bytes_chunck = n.recv(2048, False)
            # user has disconnected
            if not bytes_chunck:
                server_down = True
                break
            full_bytes += bytes_chunck

            WINDOW.fill(Colors.BLACK)
            write(
                WINDOW,
                f"Recieving other users from server. - {round(len(full_bytes)/size * 100)}%",
                WIDTH / 2,
                HEIGHT / 2,
            )

        if server_down:
            raise Exception("SERVER CRASHED UNEXPECTEDLY")

        active_users = json.loads(full_bytes.decode("utf-8"))

        return active_users

    except Exception as e:
        global run
        print("COULD NOT GET ACTIVE USRERS FROM SERVER.", e)
        print("DATA RECIEVED WAS: ", data)
        run = False


# move b/w pages
def prev_page(*args, **kwargs):
    global current_display, displays
    current_display -= 1 if current_display > 0 else 0


def add_page(page):
    global current_display, displays
    if page in displays:
        displays.remove(page)
    displays.append(page)
    current_display = len(displays) - 1


def go_to_home(*args, **kwargs):
    global current_display, displays
    add_page("home")


def next_page(*args, **kwargs):
    global current_display, displays
    if current_display < len(displays) - 1:
        current_display += 1


# go to the settings page
def go_to_settings(*args, **kwargs):
    global current_display, displays
    add_page("settings")


# send something to the server
def send(data, pickle_data=True):
    sent = n.send(data, pickle_data)
    return sent


# cancel challenge
def cancel_challenge(button=None, on_close=None, *args, **kwargs):
    req = {}
    req["cancel_challenge"] = kwargs
    send(req)
    if on_close:
        on_close()


# accept challenge from another user
def accept_challenge(on_close=None, *args, **kwargs):
    req = {}
    req["accepted"] = {
        "player1_id": kwargs.get("challenger_id"),
        "player2_id": curr_user_id,
        "game": kwargs.get("game"),
    }
    send(req)
    if on_close:
        on_close()


# reject a challenge from another user
def reject_challenge(on_close=None, *args, **kwargs):
    req = {}
    req["rejected"] = {
        "player1_id": kwargs.get("challenger_id"),
        "player2_id": curr_user_id,
        "game": kwargs.get("game"),
    }
    send(req)
    if on_close:
        on_close()


# change display when a profile is closed
def on_profile_close(**kwargs):
    go_to_home()


# change display to user profile
def on_user_button_click(user_button, **kwargs):
    global active_profile
    active_profile = user_profiles[
        user_button.id
    ]  # this button id is same as that user's id
    add_page("user_profile")


# send a payload to the server when the user challenges someone
def on_challenge_button_click(challenge_to, game, **kwargs):
    req = {}
    req["challenge"] = (challenge_to, game)  # (challenged_id, game_name)
    send(req)


# quit a gmae
def quit_game(button=None, **kwargs):

    if active_game and not active_game.game_over:
        quit_req = {}
        quit_req["quit"] = game_details.get("game_id")
        send(quit_req)

    go_to_home()


# move/place a piece
def move(button=None, *args, **kwargs):
    move_req = {}
    move_req["move"] = button.id
    send(move_req)


# send an update details request
def send_update_details_request(changed, *args, **kwargs):
    req = {}
    req["updated"] = changed
    send(req)


# send an image in batches
def send_image(img):
    WINDOW.fill(Colors.BLACK)
    write(WINDOW, f"Uploading Image - {0}%", WIDTH / 2, HEIGHT / 2)

    image_bytes = img.tobytes()
    size = len(image_bytes)

    # send the server the size of the image
    send({"image": {"size": size, "shape": img.shape, "dtype": img.dtype}})

    allowed = n.recv()
    if not allowed.get(
        "image_allowed"
    ):  # image is prolly too large, and rejected by server
        popups["error"].add_popup("Error", allowed.get("error"), text_color=Colors.RED)

    else:
        time.sleep(1)

        # print("started sending image")
        # send the image bytes
        for batch in range(0, size, 2048):
            check_quit()
            send(image_bytes[batch : batch + 2048], pickle_data=False)
            WINDOW.fill(Colors.BLACK)
            write(
                WINDOW,
                f"Uploading Image - {round((batch+2048)/size * 100)}%",
                WIDTH / 2,
                HEIGHT / 2,
            )

        # print("done sending image")


# what happens when the user changes profile pic
def on_image_change(path, *args, **kwargs):

    try:
        with open(path) as f:
            img = pygame.image.load(f)
            img = pygame.surfarray.array3d(pygame.transform.scale(img, (img_w, img_h),))

            send_image(img)

    except Exception as e:
        popups["error"].add_popup(
            "Error", str(e), text_color=Colors.RED,
        )
        if saved_settings["sound_effects"]:
            Sound_Effects.error.play()


# add an user to the active users
def add_user(user_data):
    user_id = user_data["id"]
    active_users[user_id] = user_data

    user_buttons.add_user_button(
        user_data, user_id == curr_user_id, on_user_button_click
    )

    user_profiles[user_id] = Profile(
        user_data,
        user_id == curr_user_id,
        on_profile_close,
        on_challenge_button_click,
        on_user_name_change=send_update_details_request,
        on_image_change=on_image_change,
    )


# generate user buttons for the home page, and also the profiles to be displayed when clicked on
def generate_users():
    # add the current user first - so it gets pinned to the top
    add_user(curr_user)

    # add buttons for all other users
    for key in active_users.keys():
        if key != curr_user_id:
            add_user(active_users[key])


# delete a user
def del_user(id):
    active_users.pop(id)
    user_buttons.remove_user_button(id)
    user_profiles.pop(id)

    if active_profile and active_profile.user["id"] == id:
        active_profile.on_disconnect()


# update user stats
def update_user(id, changed):
    for key in changed:
        if id == curr_user_id:
            curr_user[key] = changed[key]

        active_users[id][key] = changed[key]

    user_buttons.update_button(id, changed)
    user_profile = user_profiles[id]
    user_profile.update(changed=changed)


# check for pygame quit
def check_quit():
    global run
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            print("USER EXIT")
            try:
                # try for a clean exit
                run = False
                mixer.music.stop()
                pygame.quit()
                quit()
            except:
                # force exit otherwise
                quit()


# recieve some data from the server
def recieve():
    global displays, current_display, game_details, active_game, game_board, run, ind, active_profile, challenge_form, popup
    while run:

        data = n.recv()
        sound_to_play = None
        # no data recieved - server is likely down.
        if not data:
            print("SERVER DOWN. OR CONNECTION LOST.")
            run = False
            break

        # a new user has connected
        if data.get("connected"):
            # data["connected"] is the details of that user
            # add the user to all required dicts
            add_user(data["connected"])

        # someone has disconnected
        if data.get("disconnected"):
            # data["disconnected"] is the id of that user
            # remove that user from all dicts
            del_user(data["disconnected"])

        # recieved a message
        if data.get("message"):
            # default props for the message
            popup_props = {
                "title": data["message"]["title"],
                "button_props": [],
            }

            # add the props for the message (if any)
            if data["message"].get("buttons"):
                for b in data["message"]["buttons"]:
                    popup_props["button_props"].append(default_buttons[b])

            if data["message"].get("text"):
                popup_props["text"] = data["message"]["text"]

            if data["message"].get("context"):
                popup_props["context"] = data["message"]["context"]

            if data["message"].get("closeable") is not None:
                popup_props["closeable"] = data["message"].get("closeable")

            if data["message"].get("id") is not None:
                popup_props["id"] = data["message"].get("id")

            # add the message to the messages section
            popups["message"].add_popup(**popup_props)

            sound_to_play = Sound_Effects.message

        # recieved an error message
        if data.get("error"):
            popups["error"].add_popup(
                "Error", data["error"], text_color=Colors.RED,
            )
            sound_to_play = Sound_Effects.error

        # new game started
        if data.get("new_game"):
            game_details = data["new_game"]["details"]  # {game_id, board}
            game_name = data["new_game"]["game"]  # game name

            # setup the game accordingly
            if game_name == "tic_tac_toe":
                game_board = TTT_Board(
                    X_id=game_details["board"].X_id,
                    O_id=game_details["board"].O_id,
                    on_button_click=move,
                    rows=game_details["board"].rows,
                    cols=game_details["board"].cols,
                )
            elif game_name == "connect4":
                game_board = Connect4_Board(
                    curr_user_id,
                    game_details["board"].red_id,
                    game_details["board"].blue_id,
                    on_button_click=move,
                    rows=game_details["board"].rows,
                    cols=game_details["board"].cols,
                )

            # create a wrapper for the game board
            active_game = Game_Template(
                curr_user_id,
                data["new_game"]["players"],
                data["new_game"]["identification_dict"],
                game_details["board"].turn_id,
                game_name,
                game_board,
                on_quit=quit_game,
            )

            add_page("game")
            sound_to_play = Sound_Effects.game_start

        # someone has moved,update on this screen
        if data.get("moved"):
            game_board.place(data["moved"]["to"], data["moved"]["turn_string"])
            active_game.set_turn(data["moved"]["turn_id"])
            sound_to_play = Sound_Effects.select

        # game over
        if data.get("game_over"):
            sound_to_play = None

            active_game.game_over_protocol(data["game_over"])

        # a user has updated their profile image

        if data.get("image"):
            size, shape, dtype, id = (
                data["image"]["size"],
                data["image"]["shape"],
                data["image"]["dtype"],
                data["image"]["user_id"],
            )
            full_image = b""
            # print("Total image bytes supposed to be recieved:", size)

            image_bytes = ""  # image will come in as bytes
            server_down = False
            while len(full_image) != size:
                if len(full_image) > size:
                    run = False
                    print("supposed to recv:", size, "recvd:", len(full_image))
                    raise Exception("SERVER CODE HAS A BUG IN SENDING IMAGE.")

                image_bytes = n.recv(2048, False)
                # user has disconnected
                if not image_bytes:
                    server_down = True
                    break
                full_image += image_bytes

            if server_down:
                continue

            # print("Total image bytes recieved: ", len(full_image))
            image = np.frombuffer(full_image, dtype=dtype).reshape(*shape)
            surf = pygame.surfarray.make_surface(image)
            changed = {"image": surf}
            update_user(id, changed)

        # update a user's details
        if data.get("updated"):
            update_user(data["updated"]["user_id"], data["updated"]["changed"])

        if saved_settings["sound_effects"] and sound_to_play:
            sound_to_play.play()

        sound_to_play = None


# draw everything
def draw(left_win, right_win, user_buttons):
    left_win.fill(Colors.BG_COLOR)
    right_win.fill(Colors.LIGHT_BROWN)

    # check the current display and draw the left pane accordingly
    if displays[current_display] == "home":
        user_buttons.draw(left_win)

    elif displays[current_display] == "user_profile":
        active_profile.draw(left_win)

    elif displays[current_display] == "game":
        active_game.draw(left_win)

    elif displays[current_display] == "settings":
        settings_page.draw(left_win)

    # draw the right side
    for p_container in popups.values():
        p_container.draw(right_win)

    navigation_buttons.draw(right_win)

    WINDOW.blit(left_win, (0, 0))
    WINDOW.blit(right_win, (LEFT_WIDTH + GAP_BETWEEN_SECTIONS, 0))
    pygame.display.update()


# setup all the variables and connect to the server
def setup(error=None):
    global n, curr_user_id, active_users, curr_user, user_buttons, user_profiles, displays, current_display, active_profile, settings_page, popups, game_board, active_game, game_details, default_buttons, navigation_buttons

    init_data = connect(error)
    if init_data:
        n, curr_user_id = init_data
    else:
        raise Exception(
            "COULD NOT CONNECT TO SERVER. PLEASE MAKE SURE YOU ARE CONNECTING TO THE RIGHT IP ADDRESS AND PORT, AND THAT YOU INTERNET IS WORKING."
        )

    WINDOW.fill(Colors.BLACK)
    pygame.display.update()

    active_users = recieve_active_users()  # load all the users

    curr_user = active_users[curr_user_id]  # load the current user
    user_buttons = UserButton_Container()  # display user buttons on home page
    user_profiles = {}  # a profile for every active user

    # display stuff
    displays = ["home"]  # a list of displays, to allow back and forth b/w them
    current_display = 0  # index of the display, from the displays list
    active_profile = None
    settings_page = Settings_Page(lambda *args, **kwargs: go_to_home())

    # popups on right side
    popups = {
        "error": Notification_Container("ERRORS", 0, 100),
        "message": Notification_Container("MESSAGES", 0, 460),
    }

    # game stuff
    game_board = None
    active_game = None
    game_details = None

    # types of buttons used in RIGHT pane / messages section
    default_buttons = {
        "cancel": {
            "color": Colors.RED,
            "styles": Button_Styles.CANCEL_BUTTON_STYLE,
            "func": cancel_challenge,
        },
        "accept": {
            "color": Colors.LIGHT_BLUE,
            "styles": Button_Styles.ACCEPT_BUTTON_STYLE,
            "func": accept_challenge,
        },
        "reject": {
            "color": Colors.RED,
            "styles": Button_Styles.REJECT_BUTTON_STYLE,
            "func": reject_challenge,
        },
    }

    navigation_buttons = Navigators(prev_page, next_page, go_to_home, go_to_settings)

    generate_users()


# main function, put everything together
def main():
    global run

    # recieve data from the server in a seperate thread
    start_new_thread(recieve, ())

    WINDOW.fill(Colors.BLACK)
    pygame.display.update()

    if saved_settings["play_music"]:
        mixer.music.play(-1)

    while run:
        # run at a controlled fps
        clock.tick(fps)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
                mixer.music.stop()
                break

            # which display is on - check for events accordingly
            if displays[current_display] == "home":
                user_buttons.check_event(e)

            elif displays[current_display] == "user_profile":
                active_profile.check_event(e)

            elif displays[current_display] == "game":
                active_game.check_event(e)

            elif displays[current_display] == "settings":
                settings_page.check_event(e)

            # check events for all popups
            for popup_container in popups.values():
                popup_container.check_event(e)

            navigation_buttons.check_event(e, current_display, displays)

        if displays[current_display] == "user_profile":
            active_profile.check_keys(pygame.key.get_pressed())

        draw(WINDOW_LEFT, WINDOW_RIGHT, user_buttons)


if __name__ == "__main__":
    setup()
    main()
    print("DISCONNECTED")
