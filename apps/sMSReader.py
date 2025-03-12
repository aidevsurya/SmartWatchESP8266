from machine import Pin, I2C, UART
from ssd1306 import SSD1306_I2C
import utime

# OLED setup
i2c = I2C(scl=Pin(5), sda=Pin(4))  # Adjust pins based on your connection
oled = SSD1306_I2C(128, 64, i2c)

# SIM800L setup
uart = UART(0, baudrate=9600, tx=Pin(1), rx=Pin(3))

# Buttons setup
btn_up = Pin(0, Pin.IN, Pin.PULL_UP)
btn_down = Pin(13, Pin.IN, Pin.PULL_UP)
btn_select = Pin(14, Pin.IN, Pin.PULL_UP)
btn_exit = Pin(0, Pin.IN, Pin.PULL_UP)

# Global variables
sms_list = []
selected_index = 0

def send_command(command, delay=1):
    """Send AT command to SIM800L and return the response."""
    uart.write(command + '\r\n')
    utime.sleep(delay)
    if uart.any():
        return uart.read().decode('utf-8')
    return ""

def check_module_connection():
    """Check if the SIM800L module is connected."""
    response = send_command("AT", 2)  # Simple AT command to check connection
    if "OK" in response:
        return True
    return False

def fetch_sms_list():
    """Fetch the list of SMS messages."""
    global sms_list
    sms_list = []
    response = send_command("AT+CMGL=\"ALL\"", 2)  # List all SMS
    if "+CMGL:" in response:
        lines = response.split("\n")
        for line in lines:
            if "+CMGL:" in line:
                parts = line.split(",")
                index = parts[0].split(":")[1].strip()
                sender = parts[2].strip('"')
                sms_list.append((index, sender))
    else:
        sms_list = []

def display_sms_list():
    """Display SMS list on OLED with scrolling."""
    oled.fill(0)
    start_index = max(0, selected_index - 2)
    for i in range(start_index, min(len(sms_list), start_index + 4)):
        marker = ">" if i == selected_index else " "
        oled.text(f"{marker}{sms_list[i][1]}", 0, (i - start_index) * 10)
    oled.show()

def read_sms(index):
    """Read an SMS by index."""
    response = send_command(f"AT+CMGR={index}", 2)
    if "+CMGR:" in response:
        return response.split("\n")[2]  # Message body
    return "Failed to read message."

def display_message(message):
    """Display a selected SMS message."""
    oled.fill(0)
    lines = [message[i:i+20] for i in range(0, len(message), 20)]
    for i, line in enumerate(lines[:6]):
        oled.text(line, 0, i * 10)
    oled.show()

# Main program
oled.fill(0)
oled.text("Checking Module...", 0, 0)
oled.show()
if check_module_connection():
    oled.fill(0)
    oled.text("Module Connected", 0, 0)
    oled.show()
    utime.sleep(2)
    fetch_sms_list()
    if not sms_list:
        oled.fill(0)
        oled.text("No messages found", 0, 0)
        oled.show()
    else:
        display_sms_list()

    while True:
        if not btn_up.value():  # Scroll up
            selected_index = max(0, selected_index - 1)
            display_sms_list()
            utime.sleep(0.2)

        if not btn_down.value():  # Scroll down
            selected_index = min(len(sms_list) - 1, selected_index + 1)
            display_sms_list()
            utime.sleep(0.2)

        if not btn_select.value():  # Select message
            index = sms_list[selected_index][0]
            message = read_sms(index)
            display_message(message)
            utime.sleep(0.2)
            while True:
                if not btn_exit.value():  # Exit message view
                    display_sms_list()
                    break
                utime.sleep(0.1)

        if not btn_exit.value():  # Exit application
            oled.fill(0)
            oled.text("Exiting...", 0, 0)
            oled.show()
            break

        utime.sleep(0.1)
else:
    oled.fill(0)
    oled.text("Module not found", 0, 0)
    oled.show()
    utime.sleep(3)  # Wait for a few seconds before restarting or taking action
