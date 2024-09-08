import pygame
import json
import time
import pickle
from pygame import mixer
import numpy as np
from network import Network
from constants import *
from utilities import *
from _thread import start_new_thread

# Initialize the display window
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
# Define surfaces for different parts of the window
# Left side for main content
WINDOW_LEFT = pygame.Surface((LEFT_WIDTH, HEIGHT))
# Right side for messages and errors
WINDOW_RIGHT = pygame.Surface((RIGHT_WIDTH, HEIGHT))

# Initialize clock and FPS
clock = pygame.time.Clock()
fps = 30
run = True  # Flag to control the main loop


# Function to render text on the screen
def write(win, string, x, y, font=Fonts.title_font, color=Colors.LIGHT_BLUE):
    text = font.render(string, False, color)
    text_rect = text.get_rect(center=(x, y))
    win.blit(text, text_rect)
    pygame.display.update()


# Function to create and handle the startup window for server connection
def start_up_window():
    # Input fields for server IP and port
    server_ip_input = Text_Input(
        50, 200, WIDTH / 2 - 100, 100, default_text="Enter IP")
    server_port_input = Text_Input(
        WIDTH / 2 + 50,
        200,
        WIDTH / 2 - 100,
        100,
        default_text="Enter Port (Number only)",
        number=True,
    )
    details = None

    # Callback function for the connect button
    def on_click(*args, **kwargs):
        return server_ip_input.get_text(), server_port_input.get_text()

    # Connect button
    connect_button = Button(
        (WIDTH / 2 - 100, HEIGHT / 2 + 100, 200, 100),
        Colors.GREEN,
        on_click,
        text="connect",
        **Button_Styles.CHALLENGE_BUTTON_STYLE,
    )
    # Main loop for the startup window
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


# Function to handle connection to the server
def connect(error=None):
    WINDOW.fill(Colors.BLACK)
    pygame.display.update()
    # Display error message if present
    if error:
        write(WINDOW, error, WIDTH / 2, 100, color=Colors.RED)
    else:
        write(WINDOW, "Enter IP and port to connect to.", WIDTH / 2, 100)

    ip, port = start_up_window()
    # Validate port number
    if not str(port).isnumeric():
        WINDOW.fill(Colors.BLACK)
        return connect(error="Port must be a valid number.")

    # Initialize network and connect to server
    n = Network(ip, int(port))
    data = n.connect()
    if data:
        curr_user_id = data
        return n, curr_user_id
    else:
        WINDOW.fill(Colors.BLACK)
        return connect(
            error="Could not connect. Please check if the IP and Port are correct."
        )


# Function to receive the list of active users from the server
def recieve_active_users():
    WINDOW.fill(Colors.BLACK)
    write(
        WINDOW, f"Receiving other users from server. - {0}%", WIDTH / 2, HEIGHT / 2)

    try:
        active_users = n.recv()
        if not active_users:
            raise Exception("SERVER CRASHED UNEXPECTEDLY")
        return active_users

    except Exception as e:
        global run
        print("COULD NOT GET ACTIVE USERS FROM SERVER.", e)
        print("DATA RECEIVED WAS: ", active_users)
        run = False


# Function to navigate to the previous page
def prev_page(*args, **kwargs):
    global current_display, displays
    current_display -= 1 if current_display > 0 else 0


# Function to add a new page to the display stack
def add_page(page):
    global current_display, displays
    if page in displays:
        displays.remove(page)
    displays.append(page)
    current_display = len(displays) - 1


# Function to navigate to the home page
def go_to_home(*args, **kwargs):
    global current_display, displays
    add_page("home")


# Function to navigate to the next page
def next_page(*args, **kwargs):
    global current_display, displays
    if current_display < len(displays) - 1:
        current_display += 1


# Function to navigate to the settings page
def go_to_settings(*args, **kwargs):
    global current_display, displays
    add_page("settings")


# Function to send data to the server
def send(data, pickle_data=True):
    sent = n.send(data, pickle_data)
    return sent


# Function to cancel a challenge
def cancel_challenge(button=None, on_close=None, *args, **kwargs):
    req = {"cancel_challenge": kwargs}
    send(req)
    if on_close:
        on_close()


# Function to accept a challenge from another user
def accept_challenge(on_close=None, *args, **kwargs):
    req = {
        "accepted": {
            "player1_id": kwargs.get("challenger_id"),
            "player2_id": curr_user_id,
            "game": kwargs.get("game"),
        }
    }
    send(req)
    if on_close:
        on_close()


# Function to reject a challenge from another user
def reject_challenge(on_close=None, *args, **kwargs):
    req = {
        "rejected": {
            "player1_id": kwargs.get("challenger_id"),
            "player2_id": curr_user_id,
            "game": kwargs.get("game"),
        }
    }
    send(req)
    if on_close:
        on_close()


# Function to handle closure of a user profile
def on_profile_close(**kwargs):
    go_to_home()


# Function to display the user profile when a user button is clicked
def on_user_button_click(user_button, **kwargs):
    global active_profile
    # Get the profile for the clicked user
    active_profile = user_profiles[user_button.id]
    add_page("user_profile")


# Function to send a challenge request to another user
def on_challenge_button_click(challenge_to, game, **kwargs):
    req = {"challenge": (challenge_to, game)}  # (challenged_id, game_name)
    send(req)


# Function to quit a game
def quit_game(button=None, **kwargs):
    if active_game and not active_game.game_over:
        quit_req = {"quit": game_details.get("game_id")}
        send(quit_req)
    go_to_home()


# Function to move or place a piece in the game
def move(button=None, *args, **kwargs):
    move_req = {
        "move": {"game_id": game_details["game_id"], "move": button.id}}
    send(move_req)


# Function to send an update request with changed details
def send_update_details_request(changed, *args, **kwargs):
    req = {"updated": changed}
    send(req)


# Function to display the upload progress of an image
def upload_screen(batch_number, n_batches):
    check_quit()
    WINDOW.fill(Colors.BLACK)
    write(
        WINDOW,
        f"Uploading Image - {round((batch_number) / n_batches * 100)}%",
        WIDTH / 2,
        HEIGHT / 2,
    )


# Function to send an image to the server in batches
def send_image(img):
    WINDOW.fill(Colors.BLACK)
    write(WINDOW, f"Uploading Image - {0}%", WIDTH / 2, HEIGHT / 2)

    image_bytes = img.tobytes()
    size = len(image_bytes)

    # Send the size and metadata of the image to the server
    send({"image": {"size": size, "shape": img.shape, "dtype": img.dtype}})

    allowed = n.recv()
    # Check if the image was accepted by the server
    if not allowed.get("image_allowed"):
        popups["error"].add_popup(
            "Error", allowed.get("error"), text_color=Colors.RED)
    else:
        print("Started sending image")
        n.send(image_bytes, pickle_data=False, fn=upload_screen)
        print("Done sending image")


# Function to handle changes to the profile picture
def on_image_change(path, *args, **kwargs):
    try:
        with open(path) as f:
            img = pygame.image.load(f)
            img = pygame.surfarray.array3d(
                pygame.transform.scale(img, (img_w, img_h)))
            send_image(img)
    except Exception as e:
        popups["error"].add_popup("Error", str(e), text_color=Colors.RED)
        if saved_settings["sound_effects"]:
            Sound_Effects.error.play()


# Function to add a new user to the active users list
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


# Function to generate user buttons and profiles for the home page
def generate_users():
    # Add the current user first to pin them to the top
    add_user(curr_user)

    # Add buttons for all other active users
    for key in active_users.keys():
        if key != curr_user_id:
            add_user(active_users[key])


# Function to remove a user from the active users list
def del_user(id):
    active_users.pop(id)
    user_buttons.remove_user_button(id)
    user_profiles.pop(id)

    if active_profile and active_profile.user["id"] == id:
        active_profile.on_disconnect()


# Function to update user statistics
def update_user(id, changed):
    for key in changed:
        if id == curr_user_id:
            curr_user[key] = changed[key]
        active_users[id][key] = changed[key]

    user_buttons.update_button(id, changed)
    user_profile = user_profiles[id]
    user_profile.update(changed=changed)


# Function to handle pygame quit event and exit the application cleanly
def check_quit():
    global run
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            print("USER EXIT")
            try:
                # Attempt a clean exit
                run = False
                mixer.music.stop()
                pygame.quit()
                quit()
            except:
                # Force exit if clean exit fails
                quit()


# Function to process received data from the server
def on_recieve(data):
    global displays, current_display, game_details, active_game, game_board, run, ind, active_profile, challenge_form, popup

    sound_to_play = None

    # Check if no data is received, indicating server might be down or connection is lost
    if not data:
        print("SERVER DOWN. OR CONNECTION LOST.")
        run = False
        return True

    # Handle a new user connection
    if data.get("connected"):
        # data["connected"] contains the details of the newly connected user
        add_user(data["connected"])

    # Handle a user disconnection
    if data.get("disconnected"):
        # data["disconnected"] contains the id of the disconnected user
        del_user(data["disconnected"])

    # Handle received message
    if data.get("message"):
        # Default properties for the message popup
        popup_props = {
            "title": data["message"]["title"],
            "button_props": [],
        }

        # Add properties for buttons in the message popup (if any)
        if data["message"].get("buttons"):
            for b in data["message"]["buttons"]:
                popup_props["button_props"].append(default_buttons[b])

        # Add additional properties for the message popup
        if data["message"].get("text"):
            popup_props["text"] = data["message"]["text"]
        if data["message"].get("context"):
            popup_props["context"] = data["message"]["context"]
        if data["message"].get("closeable") is not None:
            popup_props["closeable"] = data["message"].get("closeable")
        if data["message"].get("id") is not None:
            popup_props["id"] = data["message"].get("id")

        # Add the message to the messages section
        popups["message"].add_popup(**popup_props)

        sound_to_play = Sound_Effects.message

    # Handle received error message
    if data.get("error"):
        popups["error"].add_popup(
            "Error", data["error"], text_color=Colors.RED,
        )
        sound_to_play = Sound_Effects.error

    # Handle the start of a new game
    if data.get("new_game"):
        # Game details {game_id, board}
        game_details = data["new_game"]["details"]
        game_name = data["new_game"]["game"]  # Game name

        # Initialize the game board based on the game type
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

        # Create a wrapper for the game board
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

    # Handle a move made by a player
    if data.get("moved"):
        game_board.place(data["moved"]["to"], data["moved"]["turn_string"])
        active_game.set_turn(data["moved"]["turn_id"])
        sound_to_play = Sound_Effects.select

    # Handle game over scenario
    if data.get("game_over"):
        sound_to_play = None
        active_game.game_over_protocol(data["game_over"])

    # Handle profile image update
    if data.get("image"):
        size, shape, dtype, id = (
            data["image"]["size"],
            data["image"]["shape"],
            data["image"]["dtype"],
            data["image"]["user_id"],
        )

        # Receive the full image data
        full_image = n.recv(load=False)

        if full_image == "":  # Server might be down
            run = False
            return True

        # Convert the received bytes into an image
        image = np.frombuffer(full_image, dtype=dtype).reshape(*shape)
        surf = pygame.surfarray.make_surface(image)
        changed = {"image": surf}
        update_user(id, changed)

    # Handle user profile updates
    if data.get("updated"):
        update_user(data["updated"]["user_id"], data["updated"]["changed"])

    # Play the corresponding sound effect if sound effects are enabled
    if saved_settings["sound_effects"] and sound_to_play:
        sound_to_play.play()

    sound_to_play = None


# Function to receive data from the server in a loop
def recieve():
    global displays, current_display, game_details, active_game, game_board, run, ind, active_profile, challenge_form, popup
    while run:
        # Receive data from the server
        data = n.recv()
        # Process the received data
        done = on_recieve(data)

        # Exit the loop if there was an issue processing the data
        if done:
            break


# Function to draw all visual elements on the screen
def draw(left_win, right_win, user_buttons):
    # Fill the left and right surfaces with their respective background colors
    left_win.fill(Colors.BG_COLOR)
    right_win.fill(Colors.LIGHT_BROWN)

    # Draw the content based on the current display
    if displays[current_display] == "home":
        # Draw user buttons on the left side for the home display
        user_buttons.draw(left_win)

    elif displays[current_display] == "user_profile":
        # Draw the active user profile on the left side
        active_profile.draw(left_win)

    elif displays[current_display] == "game":
        # Draw the active game board on the left side
        active_game.draw(left_win)

    elif displays[current_display] == "settings":
        # Draw the settings page on the left side
        settings_page.draw(left_win)

    # Draw all popups on the right side
    for p_container in popups.values():
        p_container.draw(right_win)

    # Draw navigation buttons on the right side
    navigation_buttons.draw(right_win)

    # Update the main window with the left and right surfaces
    WINDOW.blit(left_win, (0, 0))
    WINDOW.blit(right_win, (LEFT_WIDTH + GAP_BETWEEN_SECTIONS, 0))
    pygame.display.update()


# Function to initialize all variables and connect to the server
def setup(error=None):
    global n, curr_user_id, active_users, curr_user, user_buttons, user_profiles, displays, current_display, active_profile, settings_page, popups, game_board, active_game, game_details, default_buttons, navigation_buttons

    # Connect to the server and initialize network
    init_data = connect(error)
    if init_data:
        n, curr_user_id = init_data
    else:
        raise Exception(
            "COULD NOT CONNECT TO SERVER. PLEASE MAKE SURE YOU ARE CONNECTING TO THE RIGHT IP ADDRESS AND PORT, AND THAT YOUR INTERNET IS WORKING."
        )

    # Fill the main window with a black color and update the display
    WINDOW.fill(Colors.BLACK)
    pygame.display.update()

    # Load all active users from the server
    active_users = recieve_active_users()

    # Load the current user's details
    curr_user = active_users[curr_user_id]

    # Initialize containers for user buttons and profiles
    user_buttons = UserButton_Container()
    user_profiles = {}

    # Initialize display settings
    displays = ["home"]  # List of display states
    current_display = 0  # Index of the current display state
    active_profile = None  # Currently active user profile
    settings_page = Settings_Page(
        lambda *args, **kwargs: go_to_home())  # Settings page

    # Initialize popups for error and message notifications
    popups = {
        "error": Notification_Container("ERRORS", 0, 100),
        "message": Notification_Container("MESSAGES", 0, 460),
    }

    # Initialize game-related variables
    game_board = None
    active_game = None
    game_details = None

    # Define types of buttons used in the messages section on the right pane
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

    # Initialize navigation buttons for moving between pages
    navigation_buttons = Navigators(
        prev_page, next_page, go_to_home, go_to_settings)

    # Generate user buttons and profiles for the home page
    generate_users()


# Main function to control the flow of the application
def main():
    global run

    # Start a separate thread to receive data from the server
    start_new_thread(recieve, ())

    # Fill the main window with a black color and update the display
    WINDOW.fill(Colors.BLACK)
    pygame.display.update()

    # Play background music if enabled in settings
    if saved_settings["play_music"]:
        mixer.music.play(-1)

    while run:
        # Control the frame rate of the game
        clock.tick(fps)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                # Exit the application if the quit event is detected
                run = False
                mixer.music.stop()
                break

            # Check for events based on the current display state
            if displays[current_display] == "home":
                user_buttons.check_event(e)

            elif displays[current_display] == "user_profile":
                active_profile.check_event(e)

            elif displays[current_display] == "game":
                active_game.check_event(e)

            elif displays[current_display] == "settings":
                settings_page.check_event(e)

            # Check events for all popups
            for popup_container in popups.values():
                popup_container.check_event(e)

            # Check events for navigation buttons
            navigation_buttons.check_event(e, current_display, displays)

        # Check for key events if the current display is the user profile
        if displays[current_display] == "user_profile":
            active_profile.check_keys(pygame.key.get_pressed())

        # Draw all elements on the screen
        draw(WINDOW_LEFT, WINDOW_RIGHT, user_buttons)


# Run the setup and main functions if this script is executed directly
if __name__ == "__main__":
    setup()
    main()
    print("DISCONNECTED")
