import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def extract_clean_bottle():
    berry_path = 'assets/bottles/bottle-berry-americano.png'
    if os.path.exists(berry_path):
        return Image.open(berry_path).convert('RGBA')

    from scipy import ndimage

    print("1. Extracting bottle from references/bottle.png...")
    raw_path = 'references/bottle_cutout_raw.png'
    if not os.path.exists(raw_path):
        from rembg import remove
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
    cropped.save(berry_path)
    cropped.save('assets/bottles/bottle-berry-americano.webp', 'WEBP', quality=90)
    print(f"Saved {berry_path} and .webp (size: {cropped.size})")
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
    classic_bottle.save('assets/bottles/bottle-latte-classic.webp', 'WEBP', quality=90)
    print(f"Saved {classic_path} and .webp")

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
    strong_bottle.save('assets/bottles/bottle-latte-strong.webp', 'WEBP', quality=90)
    print(f"Saved {strong_path} and .webp")

    # 3. Matcha Latte
    matcha_r = np.clip(lum * 1.05 * 255 + 38, 0, 255)
    matcha_g = np.clip(lum * 1.45 * 255 + 55, 0, 255)
    matcha_b = np.clip(lum * 0.65 * 255 + 20, 0, 255)

    arr_matcha = arr.copy()
    for i, comp in enumerate([matcha_r, matcha_g, matcha_b]):
        arr_matcha[:, :, i] = arr[:, :, i] * (1.0 - liquid_weight) + comp * liquid_weight

    matcha_bottle = Image.fromarray(np.clip(arr_matcha, 0, 255).astype(np.uint8))
    matcha_ref = Image.open('references/arn-matcha-latte-strong.png').convert('RGBA')
    matcha_label = matcha_ref.resize((lw, lh), Image.Resampling.LANCZOS)

    ma_arr = np.array(matcha_label, dtype=np.float32)
    for i in range(3):
        ma_arr[:, :, i] = np.clip(ma_arr[:, :, i] + shine_arr * 28.0, 0, 255)
    matcha_label_gloss = Image.fromarray(ma_arr.astype(np.uint8))

    matcha_bottle.paste(matcha_label_gloss, (lx1, ly1), label_mask_feathered)
    matcha_path = 'assets/bottles/bottle-matcha-latte.png'
    matcha_bottle.save(matcha_path)
    matcha_bottle.save('assets/bottles/bottle-matcha-latte.webp', 'WEBP', quality=90)
    print(f"Saved {matcha_path} and .webp")

    # 4. Butterscotch Latte
    bs_r = np.clip(lum * 1.65 * 255 + 58, 0, 255)
    bs_g = np.clip(lum * 1.28 * 255 + 32, 0, 255)
    bs_b = np.clip(lum * 0.72 * 255 + 12, 0, 255)

    arr_bs = arr.copy()
    for i, comp in enumerate([bs_r, bs_g, bs_b]):
        arr_bs[:, :, i] = arr[:, :, i] * (1.0 - liquid_weight) + comp * liquid_weight

    bs_bottle = Image.fromarray(np.clip(arr_bs, 0, 255).astype(np.uint8))
    
    # Process butterscotch reference label if needed
    bs_ref_path = 'references/arn-butterscotch-latte.png'
    if not os.path.exists(bs_ref_path):
        raw_bs = Image.open('references/arn-butterscotch-latte.jpg')
        bw_raw, bh_raw = raw_bs.size
        target_h = int(bw_raw * 1066 / 797)
        pad_top = int((target_h - bh_raw) * 0.7)
        pad_bottom = target_h - bh_raw - pad_top
        top_color = tuple(np.array(raw_bs)[0, :, :].mean(axis=0).astype(int))
        bottom_color = tuple(np.array(raw_bs)[-1, :, :].mean(axis=0).astype(int))
        new_bs = Image.new('RGB', (bw_raw, target_h), top_color)
        draw_bs = ImageDraw.Draw(new_bs)
        draw_bs.rectangle([0, bh_raw + pad_top, bw_raw, target_h], fill=bottom_color)
        new_bs.paste(raw_bs, (0, pad_top))
        new_bs.save(bs_ref_path)

    bs_ref = Image.open(bs_ref_path).convert('RGBA')
    bs_label = bs_ref.resize((lw, lh), Image.Resampling.LANCZOS)

    bs_arr = np.array(bs_label, dtype=np.float32)
    for i in range(3):
        bs_arr[:, :, i] = np.clip(bs_arr[:, :, i] + shine_arr * 28.0, 0, 255)
    bs_label_gloss = Image.fromarray(bs_arr.astype(np.uint8))

    bs_bottle.paste(bs_label_gloss, (lx1, ly1), label_mask_feathered)
    bs_path = 'assets/bottles/bottle-butterscotch.png'
    bs_bottle.save(bs_path)
    bs_bottle.save('assets/bottles/bottle-butterscotch.webp', 'WEBP', quality=90)
    print(f"Saved {bs_path} and .webp")

    return classic_bottle, strong_bottle, matcha_bottle, bs_bottle

def build_carousel_cards(berry_bottle, classic_bottle, strong_bottle, matcha_bottle, bs_bottle):
    print("3. Generating updated carousel cards in assets/cards/...")
    os.makedirs('assets/cards', exist_ok=True)
    bottles = [
        (berry_bottle, 'assets/cards/card-berry-americano', (128, 22, 37)),
        (classic_bottle, 'assets/cards/card-latte-classic', (165, 113, 60)),
        (strong_bottle, 'assets/cards/card-latte-strong', (84, 37, 10)),
        (matcha_bottle, 'assets/cards/card-matcha-latte', (54, 108, 48)),
        (bs_bottle, 'assets/cards/card-butterscotch', (180, 115, 30))
    ]

    for bottle_img, out_prefix, bg_tint in bottles:
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
        png_path = f"{out_prefix}.png"
        webp_path = f"{out_prefix}.webp"
        card.save(png_path)
        card.save(webp_path, 'WEBP', quality=90)
        print(f"Saved card: {png_path} and {webp_path}")

def main():
    berry_bottle = extract_clean_bottle()
    classic_bottle, strong_bottle, matcha_bottle, bs_bottle = build_variant_bottles(berry_bottle)
    build_carousel_cards(berry_bottle, classic_bottle, strong_bottle, matcha_bottle, bs_bottle)
    print("All bottle assets generated successfully!")

if __name__ == '__main__':
    main()
