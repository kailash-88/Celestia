from PIL import Image, ImageDraw
import os

def create_app_icon(size):
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background rounded rectangle / circle
    radius = int(size * 0.22)
    padding = int(size * 0.05)
    
    # Gradient or solid brand color: MediMitra primary #0284c7
    primary_color = (2, 132, 199, 255)
    dark_primary = (3, 105, 161, 255)
    
    # Draw background squircle
    draw.rounded_rectangle(
        [(padding, padding), (size - padding, size - padding)],
        radius=radius,
        fill=primary_color
    )

    # Draw medical cross in center with subtle heart / pulse
    center_x = size // 2
    center_y = size // 2
    
    cross_width = int(size * 0.16)
    cross_len = int(size * 0.48)
    
    # Vertical bar of cross
    draw.rounded_rectangle(
        [(center_x - cross_width // 2, center_y - cross_len // 2),
         (center_x + cross_width // 2, center_y + cross_len // 2)],
        radius=cross_width // 4,
        fill=(255, 255, 255, 255)
    )
    # Horizontal bar of cross
    draw.rounded_rectangle(
        [(center_x - cross_len // 2, center_y - cross_width // 2),
         (center_x + cross_len // 2, center_y + cross_width // 2)],
        radius=cross_width // 4,
        fill=(255, 255, 255, 255)
    )
    
    # Draw a small cyan accent pulse line across the center
    pulse_thickness = max(2, int(size * 0.035))
    pulse_color = (2, 132, 199, 255)
    
    # Points for heartbeat inside the cross
    y = center_y
    step = cross_len // 6
    points = [
        (center_x - step * 2, y),
        (center_x - step, y),
        (center_x - step // 2, y - int(step * 0.9)),
        (center_x, y + int(step * 0.9)),
        (center_x + step // 2, y - int(step * 0.5)),
        (center_x + step, y),
        (center_x + step * 2, y)
    ]
    draw.line(points, fill=pulse_color, width=pulse_thickness, joint="curve")

    return img

os.makedirs('d:/Celestia/MediMitra/static/images', exist_ok=True)
icon192 = create_app_icon(192)
icon192.save('d:/Celestia/MediMitra/static/images/icon-192.png')

icon512 = create_app_icon(512)
icon512.save('d:/Celestia/MediMitra/static/images/icon-512.png')

print("Created 192x192 and 512x512 icons in static/images/")
