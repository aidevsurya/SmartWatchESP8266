from machine import Pin, ADC, I2C
import ssd1306
import time

# Initialize I2C for OLED
i2c = I2C(scl=Pin(5), sda=Pin(4))  # D1=GPIO5 (SCL), D2=GPIO4 (SDA)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize ADC on A0
adc = ADC(0)  # NodeMCU has one ADC (A0)

# Graph variables
graph_width = 128
graph_height = 64
data_points = [0] * graph_width  # Store ADC readings for the graph

# Button setup (Pin 0)
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Function to normalize ADC value to OLED height
def normalize_adc(value, max_adc=1023, height=graph_height):
    return height - int((value / max_adc) * height)

# Function to update the graph with new ADC data
def update_graph(new_value):
    global data_points

    # Shift the graph to the left
    for i in range(graph_width - 1):
        data_points[i] = data_points[i + 1]

    # Add the new value to the end
    data_points[-1] = new_value

# Function to draw the graph on OLED
def draw_graph():
    oled.fill(0)  # Clear the display

    # Draw the graph line
    for x in range(1, graph_width):
        oled.line(x - 1, data_points[x - 1], x, data_points[x], 1)

    # Update the display
    oled.show()

# Main loop
def main():
    try:
        while True:
            if button.value() == 0:  # Button pressed (active low)
                print("Button pressed, exiting.")
                oled.fill(0)
                oled.text("Exiting...", 0, 0)
                oled.show()
                time.sleep(2)
                break
            
            # Read ADC value
            adc_value = adc.read()

            # Normalize the ADC value for graphing
            normalized_value = normalize_adc(adc_value)

            # Update the graph data
            update_graph(normalized_value)

            # Draw the graph on the OLED
            draw_graph()

            # Small delay for stability
            time.sleep(0.05)
    except:
        print("Program stopped.")

main()
