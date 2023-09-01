import time
import subprocess
import sys


desired_time = "18:48"

while True:
    #current time
    current_time = time.strftime("%H:%M")


    if current_time == desired_time:
        try:
            # Full path to the Python interpreter you want to use
            python_executable = sys.executable

            # Run main.py to store the links in links.json
            subprocess.run([python_executable, "main.py"])

            # Run beautifulsoup.py to scrape data using the links from links.json
            subprocess.run([python_executable, "beautifulsoup.py"])
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        # Sleep for a while to avoid running the script multiple times
        time.sleep(60)

    # Sleep for a minute before checking the time again
    time.sleep(60)



