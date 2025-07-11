import os
import time
import random
import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Setup folder paths
base_dir = os.getcwd()
meme_folder = os.path.join(base_dir, "telegram_content", "memes")
captions_file = os.path.join(base_dir, "telegram_content", "captions.txt")
chrome_profile_dir = os.path.join(base_dir, "chrome", "igfb_profile")
image_dir = os.path.join(base_dir, "button_images")

# Load button images
def wait_and_click(image_name, timeout=15, confidence=0.8):
    path = os.path.join(image_dir, image_name)
    start = time.time()
    while time.time() - start < timeout:
        location = pyautogui.locateCenterOnScreen(path, confidence=confidence)
        if location:
            pyautogui.click(location)
            return True
        time.sleep(1)
    raise Exception(f"❌ Couldn't find {image_name} on screen.")

# Setup Chrome
options = Options()
options.add_argument(f"--user-data-dir={chrome_profile_dir}")
options.add_argument("--profile-directory=Default")
driver = webdriver.Chrome(options=options)

# Open Instagram
driver.get("https://www.instagram.com/")
time.sleep(10)

# Step 1: Click '+' (create post)
wait_and_click("create.png")

# Step 2: Click 'Select from computer'
time.sleep(3)
wait_and_click("select.png")

# Step 3: Upload meme
meme_file = random.choice([f for f in os.listdir(meme_folder) if f.endswith((".jpg", ".png"))])
meme_path = os.path.abspath(os.path.join(meme_folder, meme_file))
pyperclip.copy(meme_path)
time.sleep(1)
pyautogui.hotkey("ctrl", "v")
pyautogui.press("enter")
print("🖼 Meme selected.")
time.sleep(7)

# Step 4: Next (Crop) → Next (Filter)
wait_and_click("next.png")
time.sleep(4)
wait_and_click("next.png")
time.sleep(5)

# Step 5: Prepare Caption
with open(captions_file, "r", encoding="utf-8") as f:
    all_captions = [line.strip() for line in f if line.strip()]
selected_caption = random.choice(all_captions)
hashtags = [
    "#BreakingNews", "#PoliticalSatire", "#CorporateDrama", "#NewsMeme", "#Politics",
    "#MediaMeme", "#Exposed", "#Scandal", "#LOLPolitics", "#DesiMeme", "#FakeNewsAlert"
]
full_caption = f"{selected_caption}\n\n{' '.join(random.sample(hashtags, 5))}"
pyperclip.copy(full_caption)

# Step 6: Paste caption
wait_and_click("text.png")
time.sleep(1)
pyautogui.hotkey("ctrl", "v")
print("✅ Caption pasted.")

# Step 7: Share
time.sleep(2)
wait_and_click("share.png")
print("🚀 Meme posted!")

# Final cleanup
time.sleep(10)
driver.quit()
