import time
import network
import ntptime
import ssd1306
from machine import Pin, I2C

# Wi-Fi credentials
WIFI_SSID = 'your_wifi_ssid'
WIFI_PASSWORD = 'your_wifi_password'

# Initialize I2C and OLED Display
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Button Setup (Pin 12 for exiting program)
button_exit = Pin(0, Pin.IN, Pin.PULL_UP)

# Global variable to store the fetched time
local_time = None  # Initialize globally

# Time Zone Offset (in hours)
TIME_ZONE_OFFSET_HOUR = 5  # Example: For India (UTC +5:30)
TIME_ZONE_OFFSET_MIN = 30

# Function to check if Wi-Fi is connected
def check_wifi_connection():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Check if already connected
    if not wlan.isconnected():
        print("Wi-Fi not connected. Attempting to connect...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection with retry
        retry_count = 0
        while not wlan.isconnected() and retry_count < 10:  # Retry up to 10 times
            oled.fill(0)
            oled.text("Connecting to Wi-Fi...", 0, 0)
            oled.text("Retrying: {}...".format(retry_count + 1), 0, 20)
            oled.show()
            time.sleep(2)
            retry_count += 1

        if wlan.isconnected():
            print("Wi-Fi connected")
            print("IP Address: ", wlan.ifconfig()[0])
        else:
            print("Wi-Fi connection failed. Please check your credentials.")
            oled.fill(0)
            oled.text("Wi-Fi connection failed", 0, 0)
            oled.show()
            time.sleep(2)
            return False  # Connection failed
    else:
        print("Wi-Fi already connected.")
        print("IP Address: ", wlan.ifconfig()[0])
        return True  # Already connected

    return wlan.isconnected()

# Function to fetch time from NTP server once with timeout
def fetch_time():
    global local_time
    try:
        # Try to sync time with NTP server
        print("Fetching time from NTP...")
        ntptime.settime()  # Sync time with NTP server
        
        # Get the current time and date (after syncing with NTP)
        local_time = time.localtime()  # Store the time locally
        print("Time fetched from NTP:", local_time)
        
        # Adjust time for the local time zone
        # Add or subtract the time zone offset
        global local_time
        local_time = (local_time[0], local_time[1], local_time[2], 
                      local_time[3] + TIME_ZONE_OFFSET_HOUR, local_time[4] + TIME_ZONE_OFFSET_MIN, local_time[5], 
                      local_time[6], local_time[7])
        
    except OSError as e:
        # Handle network or NTP sync errors
        print("Error fetching time:", e)
        oled.fill(0)
        oled.text("Error fetching time", 0, 0)
        oled.show()
        time.sleep(2)

# Function to display time and date in 12-hour format
def display_time_and_date():
    global local_time  # Access the global variable
    while True:
        if local_time:
            # Get the current time and date (using locally stored time)
            hours = local_time[3]
            minutes = local_time[4]
            seconds = local_time[5]
            day = local_time[2]
            month = local_time[1]
            year = local_time[0]

            # Convert 24-hour format to 12-hour format
            if hours > 12:
                hours -= 12
                am_pm = "PM"
            elif hours == 0:
                hours = 12
                am_pm = "AM"
            elif hours == 12:
                am_pm = "PM"
            else:
                am_pm = "AM"

            # Clear the OLED screen and display time and date
            oled.fill(0)
            oled.text("   {:02d}/{:02d}/{}".format(day, month, year), 0, 0)
            oled.text("   {:02d}:{:02d}:{:02d} {}".format(hours, minutes, seconds, am_pm), 0, 20)
            oled.show()

            # Update the time by incrementing seconds manually
            local_time = time.localtime(time.mktime(local_time) + 1)  # Increment time by 1 second

        # Check if the exit button is pressed
        if button_exit.value() == 0:
            oled.fill(0)
            oled.text("Exiting Program...", 0, 0)
            oled.show()
            time.sleep(1)
            break  # Exit the loop and the program

        time.sleep(1)  # Update every second

# Run the main function
def main():
    check_wifi_connection()  # Check Wi-Fi connection
    fetch_time()  # Fetch time from NTP once
    display_time_and_date()  # Display time and date, updating every second

main()
