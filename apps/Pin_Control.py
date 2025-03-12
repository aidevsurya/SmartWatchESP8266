from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
import time

# Pin assignments
UP_BTN = 0
DOWN_BTN = 14
SELECT_BTN = 13
BACK_BTN = 12
PINS = [2, 15]  # Only pins 1 and 15 globally

# Initialize I2C and OLED display
i2c = I2C(scl=Pin(5), sda=Pin(4))  # Adjust pins if needed
oled = SSD1306_I2C(128, 64, i2c)

# Button setup
btn_up = Pin(UP_BTN, Pin.IN, Pin.PULL_UP)
btn_down = Pin(DOWN_BTN, Pin.IN, Pin.PULL_UP)
btn_select = Pin(SELECT_BTN, Pin.IN, Pin.PULL_UP)
btn_back = Pin(BACK_BTN, Pin.IN, Pin.PULL_UP)

# Menu variables
menu = ["Output", "Input", "PWM"]
current_menu_index = 0
submenu_active = False
submenu_option = None
current_pin_index = 0
pwm_objects = {}

# Function to display the menu
def display_menu():
    oled.fill(0)
    oled.text("Menu:", 0, 0)
    for i, item in enumerate(menu):
        prefix = "> " if i == current_menu_index else "  "
        oled.text(prefix + item, 0, 10 + i * 10)
    oled.show()

# Function to control GPIO as Output
def gpio_output():
    global current_pin_index
    output_pins = [1, 2, 3, 15, 16]  # Only pins 1 and 15 globally
    oled.fill(0)
    oled.text("Output Control", 0, 0)
    for i, pin in enumerate(output_pins):
        state = Pin(pin, Pin.OUT).value()
        prefix = "> " if i == current_pin_index else "  "
        oled.text(f"{prefix}Pin {pin}: {state}", 0, 10 + i * 10)
    oled.show()

    if not btn_up.value():
        current_pin_index = (current_pin_index - 1) % len(output_pins)
        time.sleep(0.2)
    elif not btn_down.value():
        current_pin_index = (current_pin_index + 1) % len(output_pins)
        time.sleep(0.2)
    elif not btn_select.value():
        pin = Pin(output_pins[current_pin_index], Pin.OUT)
        pin.value(1 if pin.value() == 0 else 0)
        time.sleep(0.2)

def gpio_input():
    oled.fill(0)
    oled.text("Input States", 0, 0)
    for i, pin in enumerate(PINS):
        pin_obj = Pin(pin, Pin.IN, Pin.PULL_UP)
        state = pin_obj.value()
        oled.text(f"Pin {pin}: {state}", 0, 10 + i * 10)
    oled.show()
    time.sleep(0.1)

# Function for PWM control
def pwm_control():
    global current_pin_index
    oled.fill(0)
    oled.text("PWM Control", 0, 0)
    for i, pin in enumerate(PINS):
        duty = pwm_objects[pin].duty() if pin in pwm_objects else 0
        prefix = "> " if i == current_pin_index else "  "
        oled.text(f"{prefix}Pin {pin}: {duty}", 0, 10 + i * 10)
    oled.show()

    if not btn_up.value():
        current_pin_index = (current_pin_index - 1) % len(PINS)
        time.sleep(0.2)
    elif not btn_down.value():
        current_pin_index = (current_pin_index + 1) % len(PINS)
        time.sleep(0.2)
    elif not btn_select.value():
        pin = PINS[current_pin_index]
        if pin not in pwm_objects:
            pwm_objects[pin] = PWM(Pin(pin), freq=1000, duty=0)
        current_duty = pwm_objects[pin].duty()
        new_duty = (current_duty + 256) % 1024
        pwm_objects[pin].duty(new_duty)
        time.sleep(0.2)
    elif not btn_back.value():
        for pwm in pwm_objects.values():
            pwm.deinit()
        pwm_objects.clear()
        time.sleep(0.2)

# Main loop
while True:
    if not submenu_active:
        display_menu()
        if not btn_up.value():
            current_menu_index = (current_menu_index - 1) % len(menu)
            time.sleep(0.2)
        elif not btn_down.value():
            current_menu_index = (current_menu_index + 1) % len(menu)
            time.sleep(0.2)
        elif not btn_select.value():
            submenu_active = True
            submenu_option = menu[current_menu_index]
            current_pin_index = 0
            time.sleep(0.2)
        elif not btn_back.value():
            break
    else:
        if submenu_option == "Output":
            gpio_output()
        elif submenu_option == "Input":
            gpio_input()
        elif submenu_option == "PWM":
            pwm_control()

        if not btn_back.value():
            submenu_active = False
            submenu_option = None
            time.sleep(0.2)
