from PIL import Image, ImageDraw
import math
import random

width, height = 1920, 1080
img = Image.new('RGB', (width, height), (10, 10, 10))
draw = ImageDraw.Draw(img)

# Dot grid pattern (Nothing style)
random.seed(42)
dot_spacing = 40
for x in range(0, width, dot_spacing):
    for y in range(0, height, dot_spacing):
        # Distance from center
        dist = math.sqrt((x - width/2)**2 + (y - height/2)**2)
        # Dots fade out near center where logo is
        if dist < 200:
            continue
        # Random opacity for organic feel
        alpha = random.randint(15, 45)
        col = (alpha, alpha, alpha)
        draw.ellipse([x-1, y-1, x+1, y+1], fill=col)

# Infinity symbol centered
cx, cy = width // 2, height // 2
r = 90
steps = 3000
stroke_color = (232, 232, 232)

# Draw with thickness by offsetting
for offset in range(-4, 5):
    for i in range(steps):
        t = (i / steps) * 2 * math.pi
        x = cx + (r * 2.5 * math.cos(t)) / (1 + math.sin(t) ** 2)
        y = cy + offset + (r * 1.4 * math.sin(t) * math.cos(t)) / (1 + math.sin(t) ** 2)
        brightness = max(0, 232 - abs(offset) * 20)
        draw.point((x, y), fill=(brightness, brightness, brightness))

# Red accent dots
for px, py in [(cx, cy), (cx + 225, cy), (cx - 225, cy)]:
    draw.ellipse([px-7, py-7, px+7, py+7], fill=(232, 39, 42))

# CENTRAL text via dots (skip — use a font)
try:
    from PIL import ImageFont
    font = ImageFont.truetype("/usr/share/fonts/liberation/LiberationSans-Regular.ttf", 20)
    text = "CENTRAL"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text(((width - text_w) / 2, cy + 130), text, fill=(100, 100, 100), font=font, spacing=8)
except:
    pass

img.save('/home/ashton/central_wallpaper.png')
print("Wallpaper saved to ~/central_wallpaper.png")
