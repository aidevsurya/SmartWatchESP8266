from machine import I2C, Pin
from ssd1306 import SSD1306_I2C
import time

# Initialize I2C for OLED (adjust pins as needed)
#i2c = I2C(scl=Pin(5), sda=Pin(4))  # Adjust SCL and SDA pins as necessary
#display = SSD1306_I2C(128, 64, i2c)

# Function to display text in big font
#display.text("AI Dev Surya",10,20,)  # Display the text
#display.show()


from network import WLAN, STA_IF
def connect_to_wifi():
    ssid = "ACCESS-DENIED"
    password = "suryahotspot"

    wlan = WLAN(STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    time.sleep(3)
    print("Local IP Address:", wlan.ifconfig()[0])  # Print the assigned IP
    
# Main loop

connect_to_wifi()

import webrepl
webrepl.start()
