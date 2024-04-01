import badger2040
import badger_os
from badger2040 import WIDTH
from utils.constants import VERSION_NUMBER, OS_NAME, GITHUB_LINK

TEXT_SIZE = 1
LINE_HEIGHT = 15

HEADER_TITLE = "System Info"

display = badger2040.Badger2040()
display.led(128)

# Clear screen
display.set_pen(15)
display.clear()


def draw_disk_usage(x):
    _, f_used, _ = badger_os.get_disk_usage()

    display.set_pen(15)
    display.image(
        bytearray(
            (
                0b00000000,
                0b00111100,
                0b00111100,
                0b00111100,
                0b00111000,
                0b00000000,
                0b00000000,
                0b00000001,
            )
        ),
        8,
        8,
        x,
        4,
    )
    display.rectangle(x + 10, 3, 80, 10)
    display.set_pen(0)
    display.rectangle(x + 11, 4, 78, 8)
    display.set_pen(15)
    display.rectangle(x + 12, 5, int(76 / 100.0 * f_used), 6)
    display.text("{:.2f}%".format(f_used), x + 91, 4, WIDTH, 1.0)


display.set_font("bitmap8")
display.set_pen(0)
display.rectangle(0, 0, WIDTH, 16)
display.set_pen(15)
display.text(HEADER_TITLE, 3, 4, WIDTH, 1)
draw_disk_usage(90)
display.text(OS_NAME, WIDTH - display.measure_text(OS_NAME, 0.4) - 4, 4, WIDTH, 1)

display.set_pen(0)

y = 16 + int(LINE_HEIGHT / 2)

display.text("Made by Devfle", 5, y, WIDTH, TEXT_SIZE)
y += LINE_HEIGHT
display.text("Developed with BadgerOS by Pimoroni", 5, y, WIDTH, TEXT_SIZE)
y += LINE_HEIGHT
y += LINE_HEIGHT
display.text(f"Current Firmware: {VERSION_NUMBER}", 5, y, WIDTH, TEXT_SIZE)
y += LINE_HEIGHT
y += LINE_HEIGHT

display.text("For more info:", 5, y, WIDTH, TEXT_SIZE)
y += LINE_HEIGHT
display.text(GITHUB_LINK, 5, y, WIDTH, TEXT_SIZE)

display.update()

# Call halt in a loop, on battery this switches off power.
# On USB, the app will exit when A+C is pressed because the launcher picks that up.
while True:
    display.keepalive()
    display.halt()
