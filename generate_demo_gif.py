#!/usr/bin/env python3
"""
Generate animated demo GIF for News Intelligence

This script creates an animated GIF showing the multi-AI scoring process.
Requires: Pillow

Usage: python generate_demo_gif.py
Output: demo.gif
"""

import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Installing Pillow...")
    os.system("pip install Pillow")
    from PIL import Image, ImageDraw, ImageFont


def create_frame(size, step, total_steps):
    """Create a single animation frame"""
    img = Image.new('RGB', size, '#0d1117')
    draw = ImageDraw.Draw(img)

    # Colors
    gold = '#ffd700'
    white = '#ffffff'
    green = '#00ff88'
    purple = '#a855f7'

    # Title
    draw.text((size[0]//2 - 160, 30), "News Intelligence", fill=gold)
    draw.text((size[0]//2 - 160, 60), "5-AI Consensus Scoring", fill=white)

    # Animation steps
    steps_text = [
        "Fetching article content...",
        "ChatGPT analyzing... Score: 8/10",
        "Claude analyzing... Score: 7/10",
        "Gemini analyzing... Score: 9/10",
        "Grok analyzing... Score: 8/10",
        "Perplexity verifying... Score: 9/10",
        "Running peer review...",
        "Consolidating opinions...",
        "Final consensus: 8.2/10"
    ]

    # Progress bar
    progress = (step + 1) / total_steps
    bar_width = 400
    bar_x = (size[0] - bar_width) // 2
    bar_y = size[1] - 80

    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + 20],
                   outline=white, width=2)

    fill_width = int(bar_width * progress)
    if fill_width > 0:
        draw.rectangle([bar_x + 2, bar_y + 2, bar_x + fill_width - 2, bar_y + 18],
                       fill=purple)

    current_text = steps_text[min(step, len(steps_text) - 1)]
    draw.text((size[0]//2 - 130, bar_y - 40), current_text, fill=white)

    y_pos = 120
    for i, text in enumerate(steps_text):
        if i < step:
            color = green
            prefix = "✓ "
        elif i == step:
            color = gold
            prefix = "→ "
        else:
            color = '#666666'
            prefix = "  "
        draw.text((80, y_pos + i * 25), prefix + text, fill=color)

    return img


def generate_demo_gif():
    """Generate the demo GIF"""
    size = (600, 450)
    total_steps = 9
    frames = []

    for step in range(total_steps):
        frame = create_frame(size, step, total_steps)
        for _ in range(3):
            frames.append(frame)

    for _ in range(5):
        frames.append(frames[-1])

    output_path = Path(__file__).parent / "demo.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=200,
        loop=0
    )

    print(f"✓ Demo GIF created: {output_path}")


if __name__ == "__main__":
    generate_demo_gif()
