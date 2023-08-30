import time
import subprocess



desired_time = "20:17"

while True:
    #current time
    current_time = time.strftime("%H:%M")


    if current_time == desired_time:
        try:

            subprocess.run(["python", "runner.py"])
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        # Sleep for a while to avoid running the script multiple times
        time.sleep(60)

    # Sleep for a minute before checking the time again
    time.sleep(60)
