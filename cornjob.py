import time
import subprocess
import sys
from datetime import datetime
from datetime import timedelta

# and the access its now method simpler
desired_time = datetime.now()

run_time =(desired_time+timedelta(minutes=2)).strftime("%H:%M")

while True:
    current_time = time.strftime("%H:%M")
    if current_time == run_time:
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