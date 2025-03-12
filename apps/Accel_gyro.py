from machine import Pin, I2C
import time
import ssd1306
from mpu6050 import MPU6050

# I2C setup
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)

# OLED setup
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# MPU-6050 setup
mpu = MPU6050(i2c)

# Button setup (Pin 0)
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Function to display data
def display_data(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z):
    oled.fill(0)  # Clear the screen

    print('Accel X: {:.2f}'.format(accel_x))
    print('Accel Y: {:.2f}'.format(accel_y))
    print('Accel Z: {:.2f}'.format(accel_z))
    print('Gyro X: {:.2f}'.format(gyro_x))
    print('Gyro Y: {:.2f}'.format(gyro_y))
    print('Gyro Z: {:.2f}'.format(gyro_z))
    
    oled.text('Accel X: {:.2f}'.format(accel_x), 0, 0)
    oled.text('Accel Y: {:.2f}'.format(accel_y), 0, 10)
    oled.text('Accel Z: {:.2f}'.format(accel_z), 0, 20)
    oled.text('Gyro X: {:.2f}'.format(gyro_x), 0, 30)
    oled.text('Gyro Y: {:.2f}'.format(gyro_y), 0, 40)
    oled.text('Gyro Z: {:.2f}'.format(gyro_z), 0, 50)
    oled.show()

# Main loop
def main():
    while True:
        if button.value() == 0:  # Button pressed (active low)
            print("Button pressed, exiting.")
            oled.fill(0)
            oled.text("Exiting...", 0, 0)
            oled.show()
            time.sleep(2)
            break

        # Get accelerometer and gyroscope data
        accel_data = mpu.get_accel_data()
        gyro_data = mpu.get_gyro_data()

        # Display accelerometer and gyroscope data on OLED
        display_data(accel_data['x'], accel_data['y'], accel_data['z'], 
                     gyro_data['x'], gyro_data['y'], gyro_data['z'])

        time.sleep(0.5)

main()
