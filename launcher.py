import gc
import os
import time
import math
import badger2040
import badger_os
import jpegdec

APP_DIR = "/apps"
FONT_SIZE = 2

changed = False
exited_to_launcher = False
woken_by_button = (
    badger2040.woken_by_button()
)  # Must be done before we clear_pressed_to_wake

if badger2040.pressed_to_wake(badger2040.BUTTON_A) and badger2040.pressed_to_wake(
    badger2040.BUTTON_C
):
    # Pressing A and C together at start quits app
    exited_to_launcher = badger_os.state_clear_running()
    badger2040.reset_pressed_to_wake()
else:
    # Otherwise restore previously running app
    badger_os.state_launch()


# init pico graphics
display = badger2040.Badger2040()
display.set_font("bitmap8")
display.led(128)

# init jpg
jpeg = jpegdec.JPEG(display.display)

# init fallback state
state = {"page": 0, "running": "launcher"}

# load state
badger_os.state_load("launcher", state)

# load apps
apps = [x[:-3] for x in os.listdir("/apps") if x.endswith(".py")]

# Approximate center lines for buttons A, B and C
centers = (41, 147, 253)

# get pages length, max 3 apps per page
MAX_PAGE = math.ceil(len(apps) / 3)


def map_value(input, in_min, in_max, out_min, out_max):
    return (((input - in_min) * (out_max - out_min)) / (in_max - in_min)) + out_min


def render():
    display.set_pen(15)
    display.clear()
    display.set_pen(0)

    # slice the apps array and get only the apps length from the current page
    # we need this to know how many icons we need to render on the current page
    max_icons = min(3, len(apps[(state["page"] * 3) :]))

    # render the menu page items
    for i in range(max_icons):
        x = centers[i]
        label = apps[i + (state["page"] * 3)]
        capitalized_label = label.upper()
        icon = f"{APP_DIR}/icon-{label}.jpg"
        jpeg.open_file(icon)
        jpeg.decode(x - 26, 30)
        display.set_pen(0)
        w = display.measure_text(capitalized_label, FONT_SIZE)
        display.text(
            capitalized_label, int(x - (w / 2)), 16 + 80, badger2040.WIDTH, FONT_SIZE
        )

    # render the menu page dots
    for i in range(MAX_PAGE):
        x = badger2040.WIDTH - 10
        y = int((128 / 2) - (MAX_PAGE * 10 / 2) + (i * 10))
        display.set_pen(0)
        display.rectangle(x, y, 8, 8)
        if state["page"] != i:
            display.set_pen(15)
            display.rectangle(x + 1, y + 1, 6, 6)

    display.update()


# blocks script as long as a button is pressed
def wait_for_user_to_release_buttons():
    while display.pressed_any():
        time.sleep(0.01)


# start apps
def start_app(index):
    wait_for_user_to_release_buttons()

    file = apps[(state["page"] * 3) + index]
    file = f"{APP_DIR}/{file}"

    for k in locals().keys():
        if k not in ("gc", "file", "badger_os"):
            del locals()[k]

    gc.collect()

    badger_os.launch(file)


# navigation logic
def button(pin):
    global changed
    changed = True

    if pin == badger2040.BUTTON_A:
        start_app(0)
    if pin == badger2040.BUTTON_B:
        start_app(1)
    if pin == badger2040.BUTTON_C:
        start_app(2)
    if pin == badger2040.BUTTON_UP:
        if state["page"] > 0:
            state["page"] -= 1
        render()
    if pin == badger2040.BUTTON_DOWN:
        if state["page"] < MAX_PAGE - 1:
            state["page"] += 1
        render()


if exited_to_launcher or not woken_by_button:
    wait_for_user_to_release_buttons()

    # reset state, we should move this in the specific app
    date_data = {"date": "(0, 0, 0, 0, 0, 0 ,0, 0)", "font_size": 2, "rtc_set": False}
    badger_os.state_load("date_data", date_data)
    date_data["rtc_set"] = False
    badger_os.state_save("date_data", date_data)

    display.set_update_speed(badger2040.UPDATE_MEDIUM)
    render()

display.set_update_speed(badger2040.UPDATE_FAST)

while True:
    # Sometimes a button press or hold will keep the system
    # powered *through* HALT, so latch the power back on.
    display.keepalive()

    if display.pressed(badger2040.BUTTON_A):
        button(badger2040.BUTTON_A)
    if display.pressed(badger2040.BUTTON_B):
        button(badger2040.BUTTON_B)
    if display.pressed(badger2040.BUTTON_C):
        button(badger2040.BUTTON_C)

    if display.pressed(badger2040.BUTTON_UP):
        button(badger2040.BUTTON_UP)
    if display.pressed(badger2040.BUTTON_DOWN):
        button(badger2040.BUTTON_DOWN)

    if changed:
        badger_os.state_save("launcher", state)
        changed = False

    display.halt()
