from machine import Pin, I2C
import ssd1306
import json
import time

# Initialize I2C and OLED
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Button setup
button_select = Pin(2, Pin.IN, Pin.PULL_UP)  # Select/Enter button
button_back = Pin(0, Pin.IN, Pin.PULL_UP)    # Back/Exit button
button_up = Pin(13, Pin.IN, Pin.PULL_UP)       # Scroll up button
button_down = Pin(14, Pin.IN, Pin.PULL_UP)    # Scroll down button

# Notes storage file
NOTES_FILE = 'notes.json'

# Global Variables
menu_options = ["Add Notes", "Exit Notes"]
notes = []  # List of notes with 'title' and 'content'
selected_item = 0  # Currently selected menu item (starts at note selection)
scroll_position = 0  # Scroll position for reading note content

# Function to load notes from EEPROM (file)
def load_notes():
    global notes
    try:
        with open(NOTES_FILE, 'r') as f:
            notes = json.load(f)
    except (OSError, ValueError):
        notes = []

# Function to save notes to EEPROM (file)
def save_notes():
    with open(NOTES_FILE, 'w') as f:
        json.dump(notes, f)

# Function to display the main menu
def display_menu():
    oled.fill(0)
    oled.rect(0, 0, 128, 64, 1)  # Border

    # Display title
    oled.text("Notes Menu", 30, 2)

    # Show the notes list first
    for i in range(3):  # Display up to 3 notes at a time
        note_index = scroll_position + i
        if note_index < len(notes):
            text = notes[note_index]['title']
            if selected_item == note_index:  # Highlight selected note
                oled.fill_rect(0, 16 * i + 16, 128, 16, 1)
                oled.text(text, 4, 16 * i + 18, 0)  # Inverted text
            else:
                oled.text(text, 4, 16 * i + 18, 1)
        else:
            break

    # Display "Add Notes" and "Exit Notes" options
    for i in range(2):
        item_index = len(notes) + i
        if item_index == selected_item:  # Highlight selected option
            oled.fill_rect(0, 16 * (i + len(notes)) + 16, 128, 16, 1)
            oled.text(menu_options[i], 4, 16 * (i + len(notes)) + 18, 0)  # Inverted text
        else:
            oled.text(menu_options[i], 4, 16 * (i + len(notes)) + 18, 1)

    oled.show()

# Function to display a note's content
def display_note():
    oled.fill(0)
    oled.rect(0, 0, 128, 64, 1)  # Border
    content = notes[selected_item]['content']
    lines = [content[i:i+15] for i in range(0, len(content), 15)]  # Split content into lines

    # Display 3 lines at a time based on scroll_position
    for i in range(3):
        line_index = scroll_position + i
        if line_index < len(lines):
            oled.text(lines[line_index], 2, 16 * i + 4)
    oled.show()

# Function to read serial input and save a new note
def add_note():
    global notes
    oled.fill(0)
    oled.text("Add Note", 30, 2)
    oled.text("Enter title:content", 0, 20)
    oled.text("via serial.", 20, 36)
    oled.text("Press Back to cancel.", 0, 50)
    oled.show()
    
    print("Add Note Mode: Enter in 'title:content' format.")
    print("Press Back to cancel.")

    while True:
        if button_pressed(button_back):  # Cancel adding a note
            print("Cancelled adding note.")
            time.sleep(0.2)  # Debounce delay
            return

        try:
            data = input().strip()  # Wait for user input
            if ':' in data:  # Validate format
                title, content = data.split(':', 1)
                notes.append({'title': title.strip(), 'content': content.strip()})
                save_notes()
                print("Note saved successfully!")
                oled.fill(0)
                oled.text("Note Saved!", 30, 28)
                oled.show()
                time.sleep(1)  # Display feedback for 1 second
                return
            else:
                print("Invalid format. Use 'title:content'.")
                time.sleep(0.5)
        except Exception as e:
            print(f"Error while adding note: {e}")
            time.sleep(0.5)

# Button debounce check
def button_pressed(pin):
    return pin.value() == 0

# Main menu navigation
def navigate():
    global selected_item, scroll_position

    in_menu = True
    while in_menu:
        display_menu()

        if button_pressed(button_up):
            if selected_item > 0:
                selected_item -= 1
                if selected_item < scroll_position:
                    scroll_position -= 1  # Scroll up through notes
            time.sleep(0.2)  # Debounce delay

        if button_pressed(button_down):
            if selected_item < len(notes) + len(menu_options) - 1:
                selected_item += 1
                if selected_item >= scroll_position + 3:
                    scroll_position += 1  # Scroll down through notes
            time.sleep(0.2)  # Debounce delay

        if button_pressed(button_select):
            if selected_item < len(notes):  # View selected note
                view_note()
                scroll_position = 0
            elif selected_item == len(notes):  # Add Notes option
                add_note()
                scroll_position = 0
            elif selected_item == len(notes) + 1:  # Exit Notes option
                print("Exiting Notes Menu.")
                in_menu = False

        if button_pressed(button_back):  # Exit on Back button press
            print("Exiting Notes Menu.")
            in_menu = False
    return

# Function to view a note
def view_note():
    global scroll_position

    in_note = True
    scroll_position = 0  # Reset scroll position
    while in_note:
        display_note()

        if button_pressed(button_up) and scroll_position > 0:
            scroll_position -= 1
            time.sleep(0.2)

        if button_pressed(button_down):
            content = notes[selected_item]['content']
            lines = [content[i:i+21] for i in range(0, len(content), 21)]
            if scroll_position < len(lines) - 3:  # Allow scrolling if more lines exist
                scroll_position += 1
                time.sleep(0.2)

        if button_pressed(button_back):
            in_note = False
            time.sleep(0.2)

# Initialize and run the program
def main():
    load_notes()
    navigate()
main()
