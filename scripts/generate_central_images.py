from PIL import Image, ImageDraw, ImageFont
import math

# Background - pure black
bg = Image.new('RGB', (1920, 1080), (10, 10, 10))
bg.save('/usr/share/plymouth/themes/central/background.png')

# Logo - infinity symbol + CENTRAL text
logo = Image.new('RGBA', (400, 200), (0, 0, 0, 0))
draw = ImageDraw.Draw(logo)

# Draw infinity using dots along the path
cx, cy = 200, 90
r = 55
steps = 1000
stroke_color = (232, 232, 232, 255)
red = (232, 39, 42, 255)

for i in range(steps):
    t = (i / steps) * 2 * math.pi
    x = cx + (r * 2.5 * math.cos(t)) / (1 + math.sin(t) ** 2)
    y = cy + (r * 1.4 * math.sin(t) * math.cos(t)) / (1 + math.sin(t) ** 2)
    draw.ellipse([x-3, y-3, x+3, y+3], fill=stroke_color)

# Red dots at key points
for px, py in [(200, 90), (338, 90), (62, 90)]:
    draw.ellipse([px-5, py-5, px+5, py+5], fill=red)

# CENTRAL text
try:
    font = ImageFont.truetype("/usr/share/fonts/liberation/LiberationSans-Regular.ttf", 28)
except:
    font = ImageFont.load_default()

text = "CENTRAL"
bbox = draw.textbbox((0, 0), text, font=font)
text_w = bbox[2] - bbox[0]
draw.text(((400 - text_w) / 2, 148), text, fill=(232, 232, 232, 255), font=font)

logo.save('/usr/share/plymouth/themes/central/logo.png')
print("Done!")
