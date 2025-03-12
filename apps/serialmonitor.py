import machine
import ssd1306
import time
import sys

# Pin assignment for button
BUTTON_PIN = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)

# I2C setup for OLED
I2C_SCL = machine.Pin(5)  # GPIO5 for SCL
I2C_SDA = machine.Pin(4)  # GPIO4 for SDA
i2c = machine.I2C(scl=I2C_SCL, sda=I2C_SDA, freq=400000)
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Setup UART for serial communication (use the correct pins for your setup)
uart = machine.UART(0, baudrate=115200, tx=1, rx=3)  # Adjust TX/RX pins as needed

# Function to display serial data on the OLED
def display_serial_data(data):
    display.fill(0)  # Clear the screen
    display.text(data, 0, 0)  # Display the data starting from top-left corner
    display.show()  # Update the display

# Wait for serial input and display it on OLED
def main():
    print("Waiting for data from serial...")

    while BUTTON_PIN.value() != 0:
        # Check if data is available from UART (serial)
        if uart.any():  # Check if there is data in the UART buffer
            serial_data = uart.read().decode('utf-8')  # Read and decode the incoming data
            display_serial_data(serial_data)  # Display the data on OLED
            time.sleep(0.1)  # Add a small delay to avoid overloading the display

# Start the program
main()
