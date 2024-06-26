import badger2040
import badger_os
import math
import time
import machine
import ntptime

display = badger2040.Badger2040()
display.led(128)

date_data = {"date": "(0, 0, 0, 0, 0, 0 ,0, 0)", "font_size": 2, "rtc_set": False}

badger_os.state_load("date_data", date_data)


def set_local_rtc():
    
    try:
        # sync the board rtc chip time to the pico RTC
        badger2040.pcf_to_pico_rtc()
    except RuntimeError:
        pass

    if date_data["rtc_set"]:
        return

    if badger2040.is_wireless():
        try:
            display.connect()
            if display.isconnected():
                ntptime.settime()
                # sync the pico RTC time to the board rtc chip
                badger2040.pico_rtc_to_pcf()

                date_data["rtc_set"] = True
                badger_os.state_save("date_data", date_data)
        except (RuntimeError, OSError) as e:
            print(f"Wireless Error: {e.value}")


def get_days_since_start():
    # get the time since config date
    start_date = time.mktime(eval(date_data["date"]))

    # get the current time from rtc
    rtc = machine.RTC()
    current_date = time.mktime(rtc.datetime())

    return str(int((current_date - start_date) / 86400))


def render_counter():
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
