import machine
import network
import ssd1306
import time

# OLED setup
i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))  # GPIO 5 (SCL), GPIO 4 (SDA)
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Button setup (GPIO 12)
button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)

def get_network_info():
    """
    Retrieve network information (IP, SSID, etc.) from the active network.
    """
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        ssid = wlan.config('essid')
        return ssid, ip
    else:
        return "Not Connected", "0.0.0.0"

def display_info(oled, ssid, ip):
    """
    Display the network SSID and IP address on the OLED screen.
    """
    oled.fill(0)  # Clear the screen
    oled.text("Network Info", 0, 0)
    oled.text(ssid, 0, 20)
    oled.text(ip, 0, 40)
    oled.show()

def main():
    """
    Main program loop.
    """
    print("Program started. Press button to exit.")
    while True:
        ssid, ip = get_network_info()
        display_info(oled, ssid, ip)
        
        # Check button state
        if button.value() == 0:  # Button pressed
            print("Button pressed, exiting program.")
            break
        
        time.sleep(1)  # Update every second

# Run the program
try:
    main()
except KeyboardInterrupt:
    print("Program interrupted.")
finally:
    oled.fill(0)
    oled.show()
    print("Program exited cleanly.")
