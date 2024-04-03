import badger2040
import badger_os
import math
import time
import ntptime

display = badger2040.Badger2040()
display.led(128)
DATE_SUCCESSFUL_SET = False

date_data = {"date": "Invalid date_data.json file", "font_size": 2}

badger_os.state_load("date_data", date_data)


def set_local_rtc():
    if badger2040.is_wireless():
        try:
            display.connect()
            if display.isconnected():
                ntptime.settime()
                badger2040.pico_rtc_to_pcf()

                global DATE_SUCCESSFUL_SET
                DATE_SUCCESSFUL_SET = True
        except (RuntimeError, OSError) as e:
            print(f"Wireless Error: {e.value}")
    else:
        # set the rtc from "Thonny" software
        badger2040.pcf_to_pico_rtc()


def get_days_since_start():
    # get the time since config date
    start_date = time.mktime(eval(date_data["date"]))

    # get the current time from rtc
    current_date = time.mktime(time.localtime())

    return str(int((current_date - start_date) / 86400))


def render_counter():
    if not DATE_SUCCESSFUL_SET:
        set_local_rtc()

    display.set_font("bitmap8")
    display.set_pen(15)
    display.clear()
    display.set_pen(0)

    days_since_start_date = get_days_since_start()

    # TODO: destructure date data
    text_width = display.measure_text(days_since_start_date, date_data["font_size"])
    text_x = math.ceil((badger2040.WIDTH - text_width) / 2)
    text_y = math.ceil((badger2040.HEIGHT - 8 * date_data["font_size"]) / 2)

    display.text(
        days_since_start_date, text_x, text_y, badger2040.WIDTH, date_data["font_size"]
    )
    display.update()


# Call halt in a loop, on battery this switches off power.
# On USB, the app will exit when A+C is pressed because the launcher picks that up.
while True:
    render_counter()
    badger2040.sleep_for(240)
    display.keepalive()
    display.halt()
