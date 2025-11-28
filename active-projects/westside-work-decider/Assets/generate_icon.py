#!/usr/bin/env python3
"""
Generate Westside Work Decider app icon.

Design concept:
- Purple to blue gradient (matching Elite/Reliable tier colors)
- Coffee cup representing remote work spots
- WiFi-style waves representing connectivity
- Location pin representing place discovery
- Clean, ADHD-friendly high contrast design
"""

from PIL import Image, ImageDraw
import math
import os

def create_gradient(width, height):
    """Create purple to blue diagonal gradient."""
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    # Colors: Purple (#8B5CF6) to Indigo (#6366F1) to Blue (#3B82F6)
    colors = [
        (139, 92, 246),   # Purple (top-left)
        (99, 102, 241),   # Indigo (middle)
        (59, 130, 246),   # Blue (bottom-right)
    ]

    for y in range(height):
        for x in range(width):
            # Diagonal gradient
            t = (x + y) / (width + height)

            if t < 0.5:
                # Purple to Indigo
                t2 = t * 2
                r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * t2)
                g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * t2)
                b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * t2)
            else:
                # Indigo to Blue
                t2 = (t - 0.5) * 2
                r = int(colors[1][0] + (colors[2][0] - colors[1][0]) * t2)
                g = int(colors[1][1] + (colors[2][1] - colors[1][1]) * t2)
                b = int(colors[1][2] + (colors[2][2] - colors[1][2]) * t2)

            pixels[x, y] = (r, g, b)

    return img

def draw_rounded_rect(draw, coords, radius, fill):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = coords
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
    draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)

def draw_coffee_cup(draw, cx, cy, scale=1.0):
    """Draw a stylized coffee cup."""
    white = (255, 255, 255)

    # Cup body
    cup_left = int(cx - 180 * scale)
    cup_right = int(cx + 100 * scale)
    cup_top = int(cy - 100 * scale)
    cup_bottom = int(cy + 180 * scale)

    # Main cup body (trapezoid shape using polygon)
    cup_points = [
        (cup_left + 20, cup_top),       # Top left
        (cup_right - 20, cup_top),      # Top right
        (cup_right - 50, cup_bottom),   # Bottom right
        (cup_left + 50, cup_bottom),    # Bottom left
    ]
    draw.polygon(cup_points, fill=white)

    # Rounded bottom
    draw.ellipse([
        cup_left + 45, cup_bottom - 40,
        cup_right - 45, cup_bottom + 40
    ], fill=white)

    # Cup handle
    handle_x = cup_right - 30
    handle_cy = cy + 30 * scale

    # Outer handle arc
    draw.arc([
        handle_x, int(handle_cy - 90 * scale),
        int(handle_x + 120 * scale), int(handle_cy + 90 * scale)
    ], -70, 70, fill=white, width=int(40 * scale))

def draw_wifi_waves(draw, cx, cy, scale=1.0):
    """Draw WiFi-style steam waves above the cup."""
    white = (255, 255, 255)

    # Three arcs representing steam/WiFi
    waves = [
        {'y_offset': -180, 'width': 120, 'opacity': 255, 'stroke': 28},
        {'y_offset': -240, 'width': 180, 'opacity': 180, 'stroke': 26},
        {'y_offset': -300, 'width': 240, 'opacity': 120, 'stroke': 24},
    ]

    for wave in waves:
        y = int(cy + wave['y_offset'] * scale)
        w = int(wave['width'] * scale)
        stroke = int(wave['stroke'] * scale)

        # Create semi-transparent white
        color = (255, 255, 255, wave['opacity'])

        draw.arc([
            cx - w, y - int(50 * scale),
            cx + w, y + int(50 * scale)
        ], 200, 340, fill=white, width=stroke)

def draw_location_pin(draw, cx, cy, scale=1.0):
    """Draw a location pin."""
    white = (255, 255, 255)

    # Pin body (teardrop shape)
    pin_size = int(70 * scale)

    # Draw circle for top of pin
    draw.ellipse([
        cx - pin_size, cy - pin_size,
        cx + pin_size, cy + pin_size
    ], fill=white)

    # Draw triangle for bottom of pin
    triangle = [
        (cx - int(pin_size * 0.7), cy + int(pin_size * 0.5)),
        (cx + int(pin_size * 0.7), cy + int(pin_size * 0.5)),
        (cx, cy + int(pin_size * 2.2)),
    ]
    draw.polygon(triangle, fill=white)

    # Inner circle (gradient color)
    inner_size = int(35 * scale)
    draw.ellipse([
        cx - inner_size, cy - inner_size,
        cx + inner_size, cy + inner_size
    ], fill=(99, 102, 241))  # Indigo

def create_app_icon(size=1024):
    """Create the complete app icon."""
    # Create gradient background
    img = create_gradient(size, size)
    draw = ImageDraw.Draw(img)

    scale = size / 1024.0
    center_x = size // 2
    center_y = size // 2 + int(50 * scale)

    # Draw WiFi waves (steam from coffee)
    draw_wifi_waves(draw, center_x - int(40 * scale), center_y, scale)

    # Draw coffee cup
    draw_coffee_cup(draw, center_x - int(20 * scale), center_y, scale)

    # Draw location pin (bottom right)
    pin_x = center_x + int(280 * scale)
    pin_y = center_y + int(180 * scale)
    draw_location_pin(draw, pin_x, pin_y, scale * 0.8)

    return img

def main():
    """Generate all required icon sizes."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_dir = os.path.join(script_dir, 'AppIcon.appiconset')
    os.makedirs(icon_dir, exist_ok=True)

    # iOS icon sizes (as of iOS 17)
    sizes = [
        (1024, 'icon_1024.png'),      # App Store
        (180, 'icon_180.png'),        # iPhone @3x
        (167, 'icon_167.png'),        # iPad Pro @2x
        (152, 'icon_152.png'),        # iPad @2x
        (120, 'icon_120.png'),        # iPhone @2x
        (87, 'icon_87.png'),          # Spotlight @3x
        (80, 'icon_80.png'),          # Spotlight @2x
        (76, 'icon_76.png'),          # iPad @1x
        (60, 'icon_60.png'),          # iPhone @1x
        (58, 'icon_58.png'),          # Settings @2x
        (40, 'icon_40.png'),          # Spotlight @1x
        (29, 'icon_29.png'),          # Settings @1x
        (20, 'icon_20.png'),          # Notification @1x
    ]

    print("Generating Westside Work Decider app icons...")

    # Generate base icon at highest resolution
    base_icon = create_app_icon(1024)

    for size, filename in sizes:
        filepath = os.path.join(icon_dir, filename)
        if size == 1024:
            base_icon.save(filepath, 'PNG')
        else:
            resized = base_icon.resize((size, size), Image.LANCZOS)
            resized.save(filepath, 'PNG')
        print(f"  Created {filename} ({size}x{size})")

    # Create Contents.json for Xcode
    contents = '''{
  "images" : [
    {
      "filename" : "icon_40.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "2x",
      "size" : "20x20"
    },
    {
      "filename" : "icon_60.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "3x",
      "size" : "20x20"
    },
    {
      "filename" : "icon_58.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "2x",
      "size" : "29x29"
    },
    {
      "filename" : "icon_87.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "3x",
      "size" : "29x29"
    },
    {
      "filename" : "icon_76.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "2x",
      "size" : "38x38"
    },
    {
      "filename" : "icon_80.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "2x",
      "size" : "40x40"
    },
    {
      "filename" : "icon_120.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "3x",
      "size" : "40x40"
    },
    {
      "filename" : "icon_120.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "2x",
      "size" : "60x60"
    },
    {
      "filename" : "icon_180.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "3x",
      "size" : "60x60"
    },
    {
      "filename" : "icon_152.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "2x",
      "size" : "76x76"
    },
    {
      "filename" : "icon_167.png",
      "idiom" : "universal",
      "platform" : "ios",
      "scale" : "2x",
      "size" : "83.5x83.5"
    },
    {
      "filename" : "icon_1024.png",
      "idiom" : "universal",
      "platform" : "ios",
      "size" : "1024x1024"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}'''

    contents_path = os.path.join(icon_dir, 'Contents.json')
    with open(contents_path, 'w') as f:
        f.write(contents)
    print(f"  Created Contents.json")

    print(f"\nDone! Icons saved to: {icon_dir}")
    print("\nTo use in Xcode:")
    print("1. Drag the AppIcon.appiconset folder into your Assets.xcassets")
    print("2. Or copy the contents into the existing AppIcon set")

if __name__ == '__main__':
    main()
