import subprocess
import time

# Step 1: Generate Meme using index.py
print("🎨 Generating Meme using index.py...")
subprocess.run(["python", "index.py"])

# Optional delay (2 sec) to ensure file is saved
time.sleep(2)

# Step 2: Post Meme to Instagram using igfbpost.py
print("🚀 Posting Meme to Instagram using igfbpost.py...")
subprocess.run(["python", "ig1.py"])
