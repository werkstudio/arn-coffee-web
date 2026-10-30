import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from rembg import remove

def extract_clean_bottle():
    print("1. Extracting bottle from references/bottle.png...")
    raw_path = 'references/bottle_cutout_raw.png'
    if not os.path.exists(raw_path):
        input_img = Image.open('references/bottle.png')
        output_img = remove(input_img)
        output_img.save(raw_path)

    img = Image.open(raw_path).convert('RGBA')
    r, g, b, a = img.split()
    alpha = np.array(a)

    binary = alpha > 40
    labeled, num_features = ndimage.label(binary)
    sizes = ndimage.sum(binary, labeled, range(num_features + 1))
    main_label = np.argmax(sizes[1:]) + 1
    bottle_binary = (labeled == main_label)

    # Dilate by 3 pixels to preserve smooth antialiased outer contour
    dilated = ndimage.binary_dilation(bottle_binary, iterations=3)
    clean_alpha = np.where(dilated, alpha, 0).astype(np.uint8)

    clean_img = Image.merge('RGBA', (r, g, b, Image.fromarray(clean_alpha)))
    bbox = clean_img.getbbox()
    
    # Margin of 40px
    margin = 40
    crop_box = (
        max(0, bbox[0] - margin),
        max(0, bbox[1] - margin),
        min(img.width, bbox[2] + margin),
        min(img.height, bbox[3] + margin)
    )
    cropped = clean_img.crop(crop_box)
    os.makedirs('assets/bottles', exist_ok=True)
    berry_path = 'assets/bottles/bottle-berry-americano.png'
    cropped.save(berry_path)
    print(f"Saved {berry_path} (size: {cropped.size})")
    return cropped

def extract_lighting_gloss(base_bottle, lx1, ly1, lx2, ly2):
    # Extract subtle lighting reflection overlay from the original bottle surface
    crop = base_bottle.crop((lx1, ly1, lx2, ly2))
    gray = crop.convert('L')
    arr = np.array(gray, dtype=np.float32)
    
    # High-pass / edge & highlight extraction
    # Subtle vertical highlight sheen on left side (x/w ~ 0.25)
    w, h = crop.size
    x_coords = np.linspace(0, 1, w)
    highlight_strip = np.exp(-((x_coords - 0.22) ** 2) / (2 * (0.12 ** 2)))
    highlight_2d = np.tile(highlight_strip, (h, 1)) * 255.0
    
    # Blur to create smooth reflection
    shine_img = Image.fromarray(np.clip(highlight_2d, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(15.0))
    return shine_img

def build_variant_bottles(base_bottle):
    print("2. Building variants for Aren Latte Classic & Strong...")
    bw, bh = base_bottle.size
    arr = np.array(base_bottle, dtype=np.float32)
    alpha = arr[:, :, 3]

    # Label box
    lx1, ly1, lx2, ly2 = 77, 540, 874, 1606
    lw, lh = lx2 - lx1, ly2 - ly1

    # Liquid mask (all bottle below cap except label)
    liquid_mask = np.zeros((bh, bw), dtype=np.float32)
    liquid_mask[390:, :] = (alpha[390:, :] > 100).astype(np.float32)
    liquid_mask[540:1606, 77:874] = 0.0

    mask_img = Image.fromarray((liquid_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.0))
    liquid_weight = np.array(mask_img, dtype=np.float32) / 255.0

    # Base luminance
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    # Label rounded mask
    label_mask = Image.new('L', (lw, lh), 0)
    draw = ImageDraw.Draw(label_mask)
    draw.rounded_rectangle([0, 0, lw, lh], radius=24, fill=255)
    label_mask_feathered = label_mask.filter(ImageFilter.GaussianBlur(1.2))

    shine_img = extract_lighting_gloss(base_bottle, lx1, ly1, lx2, ly2)
    shine_arr = np.array(shine_img, dtype=np.float32) / 255.0

    # 1. Aren Latte Classic
    classic_r = np.clip(lum * 1.6 * 255 + 50, 0, 255)
    classic_g = np.clip(lum * 1.3 * 255 + 30, 0, 255)
    classic_b = np.clip(lum * 0.9 * 255 + 15, 0, 255)

    arr_classic = arr.copy()
    for i, comp in enumerate([classic_r, classic_g, classic_b]):
        arr_classic[:, :, i] = arr[:, :, i] * (1.0 - liquid_weight) + comp * liquid_weight

    classic_bottle = Image.fromarray(np.clip(arr_classic, 0, 255).astype(np.uint8))
    classic_ref = Image.open('references/arn-latte-classic.png').convert('RGBA')
    classic_label = classic_ref.resize((lw, lh), Image.Resampling.LANCZOS)
    
    # Add subtle plastic gloss to label
    cl_arr = np.array(classic_label, dtype=np.float32)
    for i in range(3):
        cl_arr[:, :, i] = np.clip(cl_arr[:, :, i] + shine_arr * 28.0, 0, 255)
    classic_label_gloss = Image.fromarray(cl_arr.astype(np.uint8))

    classic_bottle.paste(classic_label_gloss, (lx1, ly1), label_mask_feathered)
    classic_path = 'assets/bottles/bottle-latte-classic.png'
    classic_bottle.save(classic_path)
    print(f"Saved {classic_path}")

    # 2. Aren Latte Strong
    strong_r = np.clip(lum * 1.35 * 255 + 35, 0, 255)
    strong_g = np.clip(lum * 0.95 * 255 + 18, 0, 255)
    strong_b = np.clip(lum * 0.55 * 255 + 8, 0, 255)

    arr_strong = arr.copy()
    for i, comp in enumerate([strong_r, strong_g, strong_b]):
        arr_strong[:, :, i] = arr[:, :, i] * (1.0 - liquid_weight) + comp * liquid_weight

    strong_bottle = Image.fromarray(np.clip(arr_strong, 0, 255).astype(np.uint8))
    strong_ref = Image.open('references/arn-latte-strong.png').convert('RGBA')
    strong_label = strong_ref.resize((lw, lh), Image.Resampling.LANCZOS)

    st_arr = np.array(strong_label, dtype=np.float32)
    for i in range(3):
        st_arr[:, :, i] = np.clip(st_arr[:, :, i] + shine_arr * 28.0, 0, 255)
    strong_label_gloss = Image.fromarray(st_arr.astype(np.uint8))

    strong_bottle.paste(strong_label_gloss, (lx1, ly1), label_mask_feathered)
    strong_path = 'assets/bottles/bottle-latte-strong.png'
    strong_bottle.save(strong_path)
    print(f"Saved {strong_path}")

    return classic_bottle, strong_bottle

def build_carousel_cards(berry_bottle, classic_bottle, strong_bottle):
    print("3. Generating updated carousel cards in assets/cards/...")
    os.makedirs('assets/cards', exist_ok=True)
    bottles = [
        (berry_bottle, 'assets/cards/card-berry-americano.png', (128, 22, 37)),
        (classic_bottle, 'assets/cards/card-latte-classic.png', (165, 113, 60)),
        (strong_bottle, 'assets/cards/card-latte-strong.png', (84, 37, 10))
    ]

    for bottle_img, out_path, bg_tint in bottles:
        # Create 512x512 card with subtle glass glow
        card = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        
        # Subtle glowing radial backdrop
        glow = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse([60, 60, 452, 452], fill=(bg_tint[0], bg_tint[1], bg_tint[2], 70))
        glow = glow.filter(ImageFilter.GaussianBlur(40.0))
        card.alpha_composite(glow)

        # Scale bottle to fit nicely in 512x512 with upright posture
        # Target height ~ 440px
        scale = 430.0 / bottle_img.height
        new_w = int(bottle_img.width * scale)
        new_h = int(bottle_img.height * scale)
        resized_bottle = bottle_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        pos_x = (512 - new_w) // 2
        pos_y = (512 - new_h) // 2 - 5

        card.alpha_composite(resized_bottle, (pos_x, pos_y))
        card.save(out_path)
        print(f"Saved card: {out_path}")

def main():
    berry_bottle = extract_clean_bottle()
    classic_bottle, strong_bottle = build_variant_bottles(berry_bottle)
    build_carousel_cards(berry_bottle, classic_bottle, strong_bottle)
    print("All bottle assets generated successfully!")

if __name__ == '__main__':
    main()
