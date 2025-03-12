import machine
import ssd1306
import random
import time

# OLED display size
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

# I2C setup (adjust pins as needed)
i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))  # Adjust SCL and SDA pins as necessary
display = ssd1306.SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c)

# Button pins
UP_BUTTON = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
LEFT_BUTTON = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
DOWN_BUTTON = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
RIGHT_BUTTON = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)

# Snake parameters
MAX_LENGTH = 100
snakeX = [0] * MAX_LENGTH
snakeY = [0] * MAX_LENGTH
snakeLength = 5
foodX = 0
foodY = 0

# Movement direction
directionX = 1
directionY = 0

# Game state
gameOver = False

# Debounce variables
lastDebounceTime = 0
debounceDelay = 50  # 50ms debounce delay

def placeFood():
    global foodX, foodY
    foodX = random.randint(0, SCREEN_WIDTH // 4) * 4
    foodY = random.randint(0, SCREEN_HEIGHT // 4) * 4

def moveSnake():
    global snakeX, snakeY, snakeLength
    # Move body
    for i in range(snakeLength - 1, 0, -1):
        snakeX[i] = snakeX[i - 1]
        snakeY[i] = snakeY[i - 1]
    # Move head
    snakeX[0] += directionX * 4
    snakeY[0] += directionY * 4

    # Check if food is eaten
    if snakeX[0] == foodX and snakeY[0] == foodY:
        if snakeLength < MAX_LENGTH:
            snakeLength += 1
        placeFood()

def checkCollision():
    global gameOver
    # Check wall collision
    if snakeX[0] < 0 or snakeX[0] >= SCREEN_WIDTH or snakeY[0] < 0 or snakeY[0] >= SCREEN_HEIGHT:
        gameOver = True
    # Check self-collision
    for i in range(1, snakeLength):
        if snakeX[0] == snakeX[i] and snakeY[0] == snakeY[i]:
            gameOver = True
            break

def handleButtonPress():
    global directionX, directionY, lastDebounceTime
    currentTime = time.ticks_ms()

    # Check UP button
    if not UP_BUTTON.value() and time.ticks_diff(currentTime, lastDebounceTime) > debounceDelay and directionY == 0:
        directionX = 0
        directionY = -1
        lastDebounceTime = currentTime
    # Check LEFT button
    elif not LEFT_BUTTON.value() and time.ticks_diff(currentTime, lastDebounceTime) > debounceDelay and directionX == 0:
        directionX = -1
        directionY = 0
        lastDebounceTime = currentTime
    # Check DOWN button
    elif not DOWN_BUTTON.value() and time.ticks_diff(currentTime, lastDebounceTime) > debounceDelay and directionY == 0:
        directionX = 0
        directionY = 1
        lastDebounceTime = currentTime
    # Check RIGHT button
    elif not RIGHT_BUTTON.value() and time.ticks_diff(currentTime, lastDebounceTime) > debounceDelay and directionX == 0:
        directionX = 1
        directionY = 0
        lastDebounceTime = currentTime

def drawGame():
    display.fill(0)

    # Draw the snake
    for i in range(snakeLength):
        display.fill_rect(snakeX[i], snakeY[i], 4, 4, 1)

    # Draw the food
    display.fill_rect(foodX, foodY, 4, 4, 1)

    # Show the updated screen
    display.show()

def showGameOver():
    display.fill(0)
    display.text("Game Over!", 30, 25, 1)
    display.show()

def setup():
    global snakeX, snakeY, snakeLength
    # Initialize snake position
    for i in range(snakeLength):
        snakeX[i] = 64 - i
        snakeY[i] = 32

    # Place initial food
    placeFood()

def main():
    global gameOver
    setup()
    
    while not gameOver:
        handleButtonPress()
        moveSnake()
        checkCollision()
        drawGame()
        time.sleep_ms(200)
    
    showGameOver()

main()
