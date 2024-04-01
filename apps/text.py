import badger2040
import badger_os
import math

display = badger2040.Badger2040()
display.led(128)

text_data = {"text": "Invalid text_data.json file", "font_size": 2}

badger_os.state_load("text_data", text_data)

display.set_font("bitmap8")
display.set_pen(15)
display.clear()
display.set_pen(0)

# TODO: destructure text data
text_width = display.measure_text(text_data["text"], text_data["font_size"])
text_x = math.ceil((badger2040.WIDTH - text_width) / 2)
text_y = math.ceil((badger2040.HEIGHT - 8 * text_data["font_size"]) / 2)

display.text(
    text_data["text"], text_x, text_y, badger2040.WIDTH, text_data["font_size"]
)
display.update()

# Call halt in a loop, on battery this switches off power.
# On USB, the app will exit when A+C is pressed because the launcher picks that up.
while True:
    display.keepalive()
    display.halt()
