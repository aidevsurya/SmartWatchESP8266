from machine import Pin, I2C
import time
import os
import ssd1306
import uos

# I2C and OLED setup
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Button setup
button_right = Pin(0, Pin.IN, Pin.PULL_UP)  # RIGHT button
button_select = Pin(2, Pin.IN, Pin.PULL_UP)  # DOWN button
button_up = Pin(13, Pin.IN, Pin.PULL_UP)  # UP button
button_down = Pin(14, Pin.IN, Pin.PULL_UP)  # LEFT button


# Global Variables
menu_items = []
selected_item = 0
max_items_on_screen = 2  # Display only 2 items per screen

# Function to update the OLED display with a border and selected apps
def update_oled():
    oled.fill(0)  # Clear the screen

    # Draw a border around the screen, leaving space for the title
    oled.rect(0, 10, 128, 54, 1)  # Border (x, y, width, height, color)

    # Display the title "@AiDevSurya" outside the border, with a margin
    title = "Ai Dev Surya"
    title_width = len(title) * 8  # Approximate width based on 6 pixels per character
    title_x = (128 - title_width) // 2  # Center the title horizontally
    oled.text(title, title_x, 2)  # Display title at the top, outside the border

    # Calculate the vertical offset to center the selected item vertically
    vertical_offset = (54 - 16 - 8) // 2  # Center the first item (height of one item + margin)

    # Show the selected items
    for i in range(max_items_on_screen):
        item_index = selected_item + i
        if item_index < len(menu_items):
            item_text = menu_items[item_index]
            item_width = len(item_text) * 6  # Approximate width based on 6 pixels per character
            item_x = (128 - item_width) // 2  # Center the item horizontally

            # Highlight the selected item with an arrow at the left side
            if i == 0:  # First item is selected, placed at the vertical center
                oled.text("-> " + item_text, 2, vertical_offset + i * 20)  # Arrow aligned left with item text
            else:  # Second item is placed below the selected one with some margin at the bottom
                oled.text(item_text, item_x, vertical_offset + (i * 20) + 10)

    oled.show()

# Function to load the app scripts from the "apps" folder
def load_apps():
    global menu_items
    menu_items = []
    try:
        files = os.listdir('/apps')
        for file in files:
            if file.endswith('.py'):
                menu_items.append(file[:-3])  # Remove .py extension
    except OSError:
        menu_items = ["No apps found!"]
    update_oled()

# Function to run a selected app script using exec()
import gc  # Import garbage collection

# Function to run a selected app script using exec() and free memory afterward
def run_selected_app():
    app_name = menu_items[selected_item]
    try:
        oled.fill(0)
        oled.text("Running " + app_name, 0, 0)
        oled.show()
        time.sleep(1)

        # Read and execute the selected script
        app_path = '/apps/' + app_name + '.py'
        with open(app_path, 'r') as f:
            script = f.read()
        
        # Create a separate namespace for execution to avoid polluting the current one
        app_namespace = {}
        exec(script, app_namespace)  # Execute the script dynamically

        # Clear the app namespace to free memory
        app_namespace.clear()

    except Exception as e:
        oled.fill(0)
        oled.text("Error: " + str(e), 0, 0)
        print("Error: " + str(e))
        oled.show()
        time.sleep(2)

    finally:
        # Trigger garbage collection to free memory
        gc.collect()
        oled.fill(0)
        oled.text("Memory cleared", 0, 0)
        oled.show()
        time.sleep(1)

# Button debounce check
def button_pressed(pin):
    return pin.value() == 0

# Main menu navigation
def navigate_menu():
    global selected_item
    while True:
        # Scroll up: move the selected item up if it's not the first one
        if button_pressed(button_up) and selected_item > 0:
            selected_item -= 1
            update_oled()
            time.sleep(0.2)  # Debounce delay
        
        # Scroll down: move the selected item down, but prevent going out of bounds
        if button_pressed(button_down) and selected_item < len(menu_items) - 1:
            selected_item += 1
            update_oled()
            time.sleep(0.2)  # Debounce delay

        # Select the current app: run the selected app
        if button_pressed(button_select):  
            run_selected_app()
            break
        
        # Go back to the app list
        if button_pressed(button_right):  
            load_apps()
            break

# Initializing the menu and loading the apps
while True:
    load_apps()
    navigate_menu()
