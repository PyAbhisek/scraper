import time
import subprocess

# Define the time at which you want the script to run daily (24-hour format)
# For example, 00:00 (midnight) in this case
desired_time = "00:00"

while True:
    # Get the current time
    current_time = time.strftime("%H:%M")

    # Check if the current time matches the desired time
    if current_time == desired_time:
        try:
            # Run your script using subprocess
            subprocess.run(["/usr/bin/python3", r"C:\Users\abhis\PycharmProjects\ultimateScrapper\runner.py"])
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        # Sleep for a while to avoid running the script multiple times
        time.sleep(60)

    # Sleep for a minute before checking the time again
    time.sleep(60)
