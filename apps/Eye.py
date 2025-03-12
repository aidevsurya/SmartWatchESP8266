import machine
import ssd1306
import time
import urandom

# OLED display setup
i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))  # D1 -> SCL, D2 -> SDA
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Back button setup
back_button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)

# Eye positions and dimensions (Larger eyes to fill the screen)
left_eye_top_left = (10, 12)  # Top-left corner of left eye
right_eye_top_left = (65, 12)  # Top-left corner of right eye
eye_width = 45
eye_height = 30
corner_radius = 10

# Helper functions to draw and fade eyes
def draw_rounded_rect(x, y, width, height, radius):
    """Draw a rounded rectangle (used for eyes)"""
    for i in range(x + radius, x + width - radius):
        for j in range(y, y + height):
            oled.pixel(i, j, 1)
    for i in range(x, x + width):
        for j in range(y + radius, y + height - radius):
            oled.pixel(i, j, 1)
    for dx in range(-radius, radius):
        for dy in range(-radius, radius):
            if dx**2 + dy**2 <= radius**2:
                oled.pixel(x + radius + dx, y + radius + dy, 1)  # Top-left corner
                oled.pixel(x + width - radius + dx, y + radius + dy, 1)  # Top-right corner
                oled.pixel(x + radius + dx, y + height - radius + dy, 1)  # Bottom-left corner
                oled.pixel(x + width - radius + dx, y + height - radius + dy, 1)  # Bottom-right corner

def draw_eye(x, y, width, height, radius, state="normal"):
    """Draw the eye with a given state: 'normal', 'blink', or 'tears'."""
    if state == "blink":
        # Smooth blink: Shrink the eyes pixel by pixel
        for i in range(height, 0, -2):  # Shrinking the height
            oled.fill_rect(x, y, width, i, 0)  # Remove the eye part
            oled.show()
            time.sleep(0.05)  # Faster shrinking
        time.sleep(0.1)  # Keep eyes closed for a short time
        for i in range(0, height, 2):  # Expanding the height to open eyes
            oled.fill_rect(x, y, width, i, 1)  # Restore the eye part
            oled.show()
            time.sleep(0.05)  # Faster expansion
    elif state == "tears":
        # Draw normal eye with a tear below
        draw_rounded_rect(x, y, width, height, radius)
        draw_rounded_rect(x + width // 2 - 2, y + height + 4, 4, 6, 2)  # Tear drop
    else:
        # Normal eye
        draw_rounded_rect(x, y, width, height, radius)

def fade_in():
    """Gradually increase the contrast to simulate a fade-in effect."""
    for i in range(0, 256, 5):
        oled.contrast(i)
        time.sleep(0.02)

def fade_out():
    """Gradually decrease the contrast to simulate a fade-out effect."""
    for i in range(255, -1, -5):
        oled.contrast(i)
        time.sleep(0.02)

def clear_screen():
    oled.fill(0)

def urandom_choice(sequence):
    """Randomly choose an item from a sequence."""
    index = urandom.getrandbits(8) % len(sequence)
    return sequence[index]

# Main loop
try:
    while True:
        if not back_button.value():  # Check if back button is pressed
            break

        # Clear the display
        clear_screen()

        # Perform fade-in effect
        fade_in()

        # Get random states for both eyes
        left_eye_state = urandom_choice(["normal", "blink", "tears"])
        right_eye_state = urandom_choice(["normal", "blink", "tears"])

        # Draw both eyes with their respective states
        draw_eye(*left_eye_top_left, eye_width, eye_height, corner_radius, state=left_eye_state)
        draw_eye(*right_eye_top_left, eye_width, eye_height, corner_radius, state=right_eye_state)

        # Update the display
        oled.show()

        # Wait for a random time between 0.5 to 1.5 seconds
        time.sleep(urandom.getrandbits(8) / 255.0 + 0.5)

        # Perform fade-out effect
        fade_out()

except KeyboardInterrupt:
    pass

# Clear the display on exit
clear_screen()
oled.show()
