import machine
import ssd1306
import time
import random

# Pins for buttons
BTN_UP = 13
BTN_LEFT = 2
BTN_DOWN = 14
BTN_RIGHT = 14

# Initialize buttons
btn_up = machine.Pin(BTN_UP, machine.Pin.IN, machine.Pin.PULL_UP)
btn_left = machine.Pin(BTN_LEFT, machine.Pin.IN, machine.Pin.PULL_UP)
btn_down = machine.Pin(BTN_DOWN, machine.Pin.IN, machine.Pin.PULL_UP)
btn_right = machine.Pin(BTN_RIGHT, machine.Pin.IN, machine.Pin.PULL_UP)

# Initialize I2C and OLED display
i2c = machine.SoftI2C(scl=machine.Pin(5), sda=machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Game variables
board = [" "] * 9  # 3x3 board
player = "X"
ai = "O"
current_pos = 0  # Current cursor position
play_again = True

# Debounce helper
def debounce(pin):
    time.sleep(0.05)  # 50ms delay
    return not pin.value()

# Draw the game board
def draw_board():
    oled.fill(0)  # Clear screen
    for i in range(9):
        x = (i % 3) * 40
        y = (i // 3) * 20
        oled.rect(x, y, 40, 20, 1)  # Draw cell
        if board[i] != " ":
            oled.text(board[i], x + 15, y + 5)
    # Highlight current position
    x = (current_pos % 3) * 40
    y = (current_pos // 3) * 20
    oled.fill_rect(x, y, 40, 20, 1)  # Highlight current position with a filled rectangle
    oled.text(board[current_pos], x + 15, y + 5, 0)  # Draw text in inverted color
    oled.show()

# Check for a winner or tie
def check_winner():
    win_positions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    for pos in win_positions:
        if board[pos[0]] == board[pos[1]] == board[pos[2]] != " ":
            return board[pos[0]]
    if " " not in board:
        return "Tie"
    return None

# AI move (Medium-level logic)
def ai_move():
    # Try to win
    for i in range(9):
        if board[i] == " ":
            board[i] = ai
            if check_winner() == ai:
                return
            board[i] = " "

    # Try to block player
    for i in range(9):
        if board[i] == " ":
            board[i] = player
            if check_winner() == player:
                board[i] = ai
                return
            board[i] = " "

    # Random move
    while True:
        i = random.randint(0, 8)
        if board[i] == " ":
            board[i] = ai
            return

# Handle button press
def handle_buttons():
    global current_pos

    if debounce(btn_up):
        if debounce(btn_down):  # Combination of UP + DOWN for select
            if board[current_pos] == " ":
                board[current_pos] = player
                return True
        elif current_pos > 2:
            current_pos -= 3
    elif debounce(btn_down):
        if current_pos < 6:
            current_pos += 3
    elif debounce(btn_left):
        if current_pos % 3 > 0:
            current_pos -= 1
    elif debounce(btn_right):
        if current_pos % 3 < 2:
            current_pos += 1
    return False

# Prompt for play again or exit
def play_again_prompt():
    global play_again
    oled.fill(0)
    oled.text("Play Again?", 10, 20)
    oled.text("UP: Yes", 10, 40)
    oled.text("DOWN: No", 10, 50)
    oled.show()

    while True:
        if debounce(btn_up):
            play_again = True
            return
        elif debounce(btn_down):
            play_again = False
            return

# Main game loop
def main():
    global board, current_pos, play_again

    while play_again:
        draw_board()

        # Player move
        if handle_buttons():
            winner = check_winner()
            if winner:
                draw_board()
                time.sleep(1)
                oled.fill(0)
                if winner == "X":
                    oled.text(f"  YOU wins!" if winner != "Tie" else "It's a tie!", 0, 30)
                else:
                    oled.text(f"  A.I. wins!" if winner != "Tie" else "It's a tie!", 0, 30)
                oled.show()
                time.sleep(3)
                play_again_prompt()
                if play_again:
                    board = [" "] * 9  # Reset board
                    current_pos = 0
                continue

            # AI move
            ai_move()
            winner = check_winner()
            if winner:
                draw_board()
                time.sleep(1)
                oled.fill(0)
                if winner == "X":
                    oled.text(f"  YOU wins!" if winner != "Tie" else "It's a tie!", 0, 30)
                else:
                    oled.text(f"  A.I. wins!" if winner != "Tie" else "It's a tie!", 0, 30)
                oled.show()
                time.sleep(3)
                play_again_prompt()
                if play_again:
                    board = [" "] * 9  # Reset board
                    current_pos = 0

# Start game
main()
