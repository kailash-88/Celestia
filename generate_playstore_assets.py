"""
Generate official Google Play Store graphics:
- 512x512 High-Resolution App Icon (no alpha)
- 1024x500 Feature Graphic Banner
"""

from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs('playstore_assets', exist_ok=True)

# 1. Generate 512x512 High-Res Icon (Google Play requirement: 32-bit PNG or 24-bit without alpha)
icon = Image.new('RGB', (512, 512), color=(11, 25, 44))
draw_icon = ImageDraw.Draw(icon)

# Subtle radial background gradient
for y in range(512):
    t = y / 512.0
    r = int(14 + t * 6)
    g = int(32 + t * 18)
    b = int(58 + t * 24)
    draw_icon.line([(0, y), (512, y)], fill=(r, g, b))

# Glowing cyan accent rounded square
accent_rect = [60, 60, 452, 452]
draw_icon.rounded_rectangle(accent_rect, radius=80, fill=(16, 42, 66), outline=(45, 212, 191), width=4)

# Draw stylized medical pill & cross
# Pill outline
draw_icon.rounded_rectangle([150, 210, 362, 302], radius=46, fill=(13, 148, 136), outline=(94, 234, 212), width=4)
# Pill separator line
draw_icon.line([(256, 210), (256, 302)], fill=(45, 212, 191), width=4)
# Pill left capsule color
draw_icon.rounded_rectangle([154, 214, 254, 298], radius=42, fill=(15, 118, 110))
# Medical Cross at the top
draw_icon.rounded_rectangle([240, 110, 272, 180], radius=6, fill=(56, 189, 248))
draw_icon.rounded_rectangle([220, 130, 292, 160], radius=6, fill=(56, 189, 248))

# Save Icon
icon.save('playstore_assets/icon_512x512.png', format='PNG')
print('512x512 Google Play Icon generated: playstore_assets/icon_512x512.png')

# 2. Generate 1024x500 Feature Graphic Banner
banner = Image.new('RGB', (1024, 500), color=(10, 22, 40))
draw_banner = ImageDraw.Draw(banner)

# Deep cyber-clinical gradient
for y in range(500):
    t = y / 500.0
    r = int(10 + t * 12)
    g = int(24 + t * 28)
    b = int(45 + t * 25)
    draw_banner.line([(0, y), (1024, y)], fill=(r, g, b))

# Ambient geometric glow
draw_banner.ellipse([700, -80, 1120, 340], fill=(15, 60, 78))
draw_banner.ellipse([800, 180, 1100, 480], fill=(13, 78, 88))
draw_banner.ellipse([-80, 250, 300, 600], fill=(18, 48, 72))

# Decorative device card mockup on right
card_rect = [660, 80, 940, 420]
draw_banner.rounded_rectangle(card_rect, radius=24, fill=(12, 28, 48), outline=(45, 212, 191), width=2)
# Card header
draw_banner.rounded_rectangle([680, 110, 920, 170], radius=12, fill=(18, 42, 68))
# Schedule lines on card
draw_banner.rounded_rectangle([680, 190, 920, 235], radius=8, fill=(16, 36, 58), outline=(56, 189, 248), width=1)
draw_banner.rounded_rectangle([680, 250, 920, 295], radius=8, fill=(16, 36, 58), outline=(45, 212, 191), width=1)
draw_banner.rounded_rectangle([680, 310, 920, 355], radius=8, fill=(16, 36, 58), outline=(245, 158, 11), width=1)

# Text and branding on left
# Title
try:
    font_large = ImageFont.truetype("arialbd.ttf", 64)
    font_sub = ImageFont.truetype("arial.ttf", 26)
    font_badge = ImageFont.truetype("arialbd.ttf", 17)
except:
    font_large = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_badge = ImageFont.load_default()

draw_banner.text((80, 110), "MediMitra", fill=(248, 250, 252), font=font_large)
draw_banner.text((80, 190), "AI Medication Safety & Adherence Platform", fill=(56, 189, 248), font=font_sub)
draw_banner.text((80, 230), "Empowering Patients • Connecting Caregivers • Assisting Doctors", fill=(148, 163, 184), font=font_sub)

# Badges
badges = [
    ("AI Strip Scanner", (13, 148, 136)),
    ("Doctor Review Queue", (2, 132, 199)),
    ("Caregiver SOS Alerts", (217, 119, 6)),
    ("Regional Voice AI", (124, 58, 237))
]

bx = 80
by = 310
for text, color in badges:
    box = [bx, by, bx + 195, by + 40]
    draw_banner.rounded_rectangle(box, radius=10, fill=(16, 36, 58), outline=color, width=2)
    draw_banner.text((bx + 18, by + 10), text, fill=(241, 245, 249), font=font_badge)
    bx += 210
    if bx > 500:
        bx = 80
        by += 50

# Save Banner
banner.save('playstore_assets/feature_graphic_1024x500.png', format='PNG')
print('1024x500 Feature Graphic generated: playstore_assets/feature_graphic_1024x500.png')
