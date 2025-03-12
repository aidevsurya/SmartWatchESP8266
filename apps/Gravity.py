import machine
import time
import ssd1306
from mpu6050 import MPU6050  # Import the mpu6050 library

# Initialize I2C and the OLED display
i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))  # Adjust for ESP8266 pins
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize MPU6050
mpu = MPU6050(i2c)

# Button on Pin 12 to exit
button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)

# Ball parameters
ball_x = 64  # Start in the middle of the screen (horizontal)
ball_y = 32  # Start in the middle of the screen (vertical)
ball_radius = 3
ball_vx = 0  # No initial horizontal velocity
ball_vy = 0  # No initial vertical velocity
gravity = 0.5  # Gravity factor (affects the downward pull)
bounce_factor = 0.7  # Bounce factor to make it bounce quickly and gently
friction = 0.98  # Friction to slow down the ball over time

# Deadzone for gyroscope readings (to ignore small fluctuations)
GYRO_DEADZONE = 0.05  # Threshold below which movement is ignored

# Function to draw a circle manually
def draw_circle(x, y, radius):
    x = int(x)  # Ensure x is an integer
    y = int(y)  # Ensure y is an integer
    for i in range(x - radius, x + radius + 1):
        for j in range(y - radius, y + radius + 1):
            if (i - x)**2 + (j - y)**2 <= radius**2:
                oled.pixel(i, j, 1)  # Draw pixel if inside the circle

# Main loop
def main():
    global ball_x,ball_y,ball_vx,ball_vy
    while True:
        # Read accelerometer and gyroscope data from MPU6050
        accel_data = mpu.get_accel_data()
        gyro_data = mpu.get_gyro_data()
        
        ax = accel_data['x']
        ay = accel_data['y']
        az = accel_data['z']
        
        gx = gyro_data['x']  # Gyroscope X axis angular velocity
        gy = gyro_data['y']  # Gyroscope Y axis angular velocity
        gz = gyro_data['z']  # Gyroscope Z axis angular velocity

        # Debug: print accelerometer and gyroscope values
        print("ax:", ax, "ay:", ay, "az:", az)
        print("gx:", gx, "gy:", gy, "gz:", gz)

        # Apply gravity to vertical velocity (ball falling downward)
        gravity_effect = gravity  # Apply gravity as a constant downward force
        ball_vy += gravity_effect  # Apply gravity to the vertical velocity

        # Apply deadzone for gyroscope readings to avoid unnecessary movement
        if abs(gx) > GYRO_DEADZONE:
            ball_vx += gx * 0.02  # Adjust horizontal speed based on gyro X (left/right tilt)
        
        if abs(gy) > GYRO_DEADZONE:
            ball_vy += gy * 0.02  # Adjust vertical speed based on gyro Y (up/down tilt)

        # Apply friction to slow the ball down
        ball_vx *= friction
        ball_vy *= friction

        # Update ball position based on velocity
        ball_x += ball_vx  # Horizontal movement is affected by gyroscope
        ball_y += ball_vy  # Vertical movement is affected by gravity and gyroscope

        # Bounce when the ball hits the top or bottom of the screen
        if ball_y >= oled.height - ball_radius:
            ball_y = oled.height - ball_radius  # Prevent going below the screen
            ball_vy = -ball_vy * bounce_factor  # Bounce with some energy loss

        if ball_y <= ball_radius:
            ball_y = ball_radius  # Prevent going above the screen
            ball_vy = -ball_vy * bounce_factor  # Bounce with some energy loss

        # Ensure ball stays within screen bounds by wrapping around (no interaction with edges)
        if ball_x >= oled.width - ball_radius:
            ball_x = oled.width - ball_radius
            ball_vx *= -1  # Reverse direction if ball goes off the right side

        if ball_x <= ball_radius:
            ball_x = ball_radius
            ball_vx *= -1  # Reverse direction if ball goes off the left side

        # Clear the screen and draw the ball
        oled.fill(0)  # Clear the display
        draw_circle(ball_x, ball_y, ball_radius)  # Draw the ball
        oled.show()

        # Check if the button on Pin 12 is pressed to exit
        if button.value() == 0:
            break  # Exit the loop if button is pressed

        time.sleep(0.01)  # Adjust for smooth animation

    oled.fill(0)
    oled.show()  # Clear the screen when exiting

main()
