import os
import time
import random
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup

# === CONFIGURATION ===
TEMPLATE_DIR = "templates"
OUTPUT_DIR = os.path.join("telegram_content", "memes")
USED_PROMPTS_FILE = "used_prompts.txt"
CAPTIONS_FILE = os.path.join("telegram_content", "captions.txt")

# === TEMPLATE THEME MAP ===
template_theme_map = {
    "drake.jpg": "preference",
    "distracted_boyfriend.jpg": "temptation",
    "change_my_mind.jpg": "opinion",
    "gru_plan.jpg": "plan_fail",
    "expanding_brain.jpg": "evolution",
}

# === HELPER FUNCTIONS ===
def get_theme_from_template(template_filename):
    return template_theme_map.get(template_filename, "default")

def load_used_prompts():
    if not os.path.exists(USED_PROMPTS_FILE):
        return set()
    with open(USED_PROMPTS_FILE, "r", encoding='utf-8') as f:
        return set(line.strip() for line in f.readlines())

def save_used_prompt(prompt):
    with open(USED_PROMPTS_FILE, "a", encoding='utf-8') as f:
        f.write(prompt.replace('\n', ' ') + '\n')

def get_reddit_prompts():
    url = "https://www.reddit.com/r/PoliticalHumor/top/?t=week"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        titles = [h.get_text().strip() for h in soup.find_all("h3") if h.get_text().strip()]
        prompts = [t for t in titles if 25 < len(t) < 110]
        return prompts
    except Exception as e:
        print("Reddit scrape error:", e)
        return []

def get_headlines():
    urls = [
        "https://www.ndtv.com/politics",
        "https://indianexpress.com/section/political-pulse/",
        "https://www.thehindu.com/news/national/politics/",
    ]
    headlines = set()
    for url in urls:
        try:
            resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(resp.text, "html.parser")
            for h in soup.find_all(["h2", "h3"]):
                text = h.get_text().strip()
                if 25 < len(text) < 110:
                    headlines.add(text)
        except Exception as e:
            print(f"Headline scrape error ({url}):", e)
    return list(headlines)

def fetch_new_prompt():
    sources = [get_reddit_prompts, get_headlines]
    random.shuffle(sources)
    for src in sources:
        prompts = src()
        random.shuffle(prompts)
        for prompt in prompts:
            clean = prompt.strip()
            if clean:
                return clean
    fallback = [
        "Why do politicians always promise more than they deliver?",
        "When the government tries to fix a problem, but makes it worse.",
        "Election season: When memes matter more than manifestos.",
        "Breaking news: Politicians caught doing politician things.",
        "The face you make when your candidate actually keeps a promise."
    ]
    return random.choice(fallback)

def best_split(prompt):
    mid = len(prompt) // 2
    split_idx = prompt.find(" ", mid)
    if split_idx == -1:
        return prompt.strip(), ""
    return prompt[:split_idx].strip(), prompt[split_idx:].strip()

def generate_caption(theme, used_prompts):
    prompt = fetch_new_prompt()
    save_used_prompt(prompt)
    return best_split(prompt)

def generate_meme(template_path, captions, output_path):
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    font_size = int(height / 15)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    top, bottom = captions
    top_lines = textwrap.wrap(top, width=30)
    y = 10
    for line in top_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((width-w)/2, y), line, font=font, fill='white', stroke_width=2, stroke_fill='black')
        y += h

    bottom_lines = textwrap.wrap(bottom, width=30)
    y = height - font_size * len(bottom_lines) - 10
    for line in bottom_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((width-w)/2, y), line, font=font, fill='white', stroke_width=2, stroke_fill='black')
        y += h

    if img.mode == "RGBA":
        img = img.convert("RGB")
    img.save(output_path)
    print(f"✅ Meme saved to: {output_path}")

def append_caption_to_file(captions):
    with open(CAPTIONS_FILE, "a", encoding="utf-8") as f:
        f.write(" | ".join(captions) + "\n")

def generate_one_meme():
    used_prompts = load_used_prompts()
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    template_filename = random.choice(os.listdir(TEMPLATE_DIR))
    theme = get_theme_from_template(template_filename)
    captions = generate_caption(theme, used_prompts)
    meme_name = f"meme_{int(time.time())}.jpg"
    meme_path = os.path.join(OUTPUT_DIR, meme_name)
    template_path = os.path.join(TEMPLATE_DIR, template_filename)
    generate_meme(template_path, captions, meme_path)
    append_caption_to_file(captions)
    return meme_path, "\n\n".join(captions)

# === MAIN CALL ===
if __name__ == "__main__":
    generate_one_meme()
