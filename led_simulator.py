import time

try:
    while True:
        # Read the input file
        with open("static/input/input.txt", "r") as file:
            input_data = file.read().strip()
            print(f"Read from input.txt: {input_data}")

        # You can add logic here to simulate LED control based on input_data
        # For example, if input_data == '1', simulate a "Red LED On" message
        # You can add similar logic for other input_data values

        # Write '0' to the input file every 3 seconds
        with open("static/input/input.txt", "w") as file:
            file.write("0\n")
            print("Wrote '0' to input.txt")

        time.sleep(5)  # Repeat every 5 seconds

        c_t = time.strftime('%H:%M:%S')
        print("c_t : ", c_t)
except Exception as e:
    print(e)
