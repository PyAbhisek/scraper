# runner.py
import subprocess

# Run main.py to store the links in links.json
subprocess.run(["python", "main.py"])

# Run beautifulsoup.py to scrape data using the links from links.json
subprocess.run(["python", "beautifulsoup.py"])



