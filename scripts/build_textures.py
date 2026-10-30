import struct
import os
import subprocess
import math

def read_bmp(path):
    with open(path, 'rb') as f:
        header = f.read(54)
        sig = header[:2]
        if sig != b'BM':
            raise ValueError(f"Not a BMP: {path}")
        dib_size, w, h, planes, bpp = struct.unpack('<IiiHH', header[14:30])
        f_size, _, offset = struct.unpack('<III', header[2:14])
        f.seek(offset)
        top_down = (h < 0)
        h = abs(h)
        row_size = (w * (bpp // 8) + 3) & ~3
        raw_data = f.read(row_size * h)
        return {
            'w': w,
            'h': h,
            'bpp': bpp,
            'top_down': top_down,
            'row_size': row_size,
            'data': raw_data
        }

def get_pixel(bmp, x, y):
    if x < 0: x = 0
    if x >= bmp['w']: x = bmp['w'] - 1
    if y < 0: y = 0
    if y >= bmp['h']: y = bmp['h'] - 1
    bytes_per_pix = bmp['bpp'] // 8
    row_idx = y if bmp['top_down'] else (bmp['h'] - 1 - y)
    offset = row_idx * bmp['row_size'] + x * bytes_per_pix
    return (bmp['data'][offset+2], bmp['data'][offset+1], bmp['data'][offset])

def save_bmp(path, w, h, pixels_rgb):
    row_size = (w * 3 + 3) & ~3
    header_size = 54
    file_size = header_size + row_size * h
    bmp = bytearray(b'BM')
    bmp += struct.pack('<III', file_size, 0, header_size)
    bmp += struct.pack('<IiiHHIiIIII', 40, w, -h, 1, 24, 0, row_size * h, 2835, 2835, 0, 0)
    
    pad_bytes = b'\x00' * (row_size - w * 3)
    with open(path, 'wb') as f:
        f.write(bmp)
        for y in range(h):
            row = bytearray()
            for x in range(w):
                r, g, b = pixels_rgb[y * w + x]
                row += bytes([b, g, r])
            row += pad_bytes
            f.write(row)

def save_rgba_bmp(path, w, h, pixels_rgba):
    # 32-bit BMP with alpha
    row_size = w * 4
    header_size = 54
    file_size = header_size + row_size * h
    bmp = bytearray(b'BM')
    bmp += struct.pack('<III', file_size, 0, header_size)
    bmp += struct.pack('<IiiHHIiIIII', 40, w, -h, 1, 32, 0, row_size * h, 2835, 2835, 0, 0)
    with open(path, 'wb') as f:
        f.write(bmp)
        for y in range(h):
            row = bytearray()
            for x in range(w):
                r, g, b, a = pixels_rgba[y * w + x]
                row += bytes([b, g, r, a])
            f.write(row)

def blend(c1, c2, alpha):
    return (
        int(c1[0] * alpha + c2[0] * (1.0 - alpha)),
        int(c1[1] * alpha + c2[1] * (1.0 - alpha)),
        int(c1[2] * alpha + c2[2] * (1.0 - alpha))
    )

def create_texture(label_bmp, green_bmp, bg_color, title_text, out_jpg):
    w, h = 2048, 2048
    pixels = [(0, 0, 0)] * (w * h)
    
    # Target can label coordinates on UV map
    # Can height: x in [80, 1115] -> 1035 px
    # Can circumference front: y in [280, 1220] -> 940 px
    x_min, x_max = 75, 1120
    y_min, y_max = 280, 1220
    lw = x_max - x_min
    lh = y_max - y_min
    feather = 40.0
    
    # Sample top corner background from label
    corner_bg = get_pixel(label_bmp, 20, 20)
    
    for y in range(h):
        for x in range(w):
            if x >= 1195:
                # Metallic can top, pull tab, bottom aluminum
                pixels[y * w + x] = get_pixel(green_bmp, x, y)
            else:
                # Can sleeve
                if x_min <= x <= x_max and y_min <= y <= y_max:
                    u = (x - x_min) / float(lw)
                    v = (y - y_min) / float(lh)
                    
                    # Inverted horizontal mapping so text reads properly
                    img_x = int((1.0 - v) * (label_bmp['w'] - 1))
                    img_y = int(u * (label_bmp['h'] - 1))
                    
                    pix = get_pixel(label_bmp, img_x, img_y)
                    
                    # Edge feathering to eliminate rectangular border
                    edge_dist_x = min(x - x_min, x_max - x)
                    edge_dist_y = min(y - y_min, y_max - y)
                    alpha = min(1.0, edge_dist_x / feather, edge_dist_y / feather)
                    
                    pixels[y * w + x] = blend(pix, bg_color, alpha)
                elif 1400 <= y <= 1900 and 200 <= x <= 1000:
                    # Back of the can: Nutrition panel / barcode area
                    # Use original nutrition panel from green_bmp tinted to brand palette
                    orig = get_pixel(green_bmp, x, y)
                    # If it's the white label in green_bmp
                    if orig[0] > 180 and orig[1] > 180 and orig[2] > 180:
                        pixels[y * w + x] = (245, 245, 240) # clean white label card
                    elif orig[0] < 50 and orig[1] < 50 and orig[2] < 50:
                        pixels[y * w + x] = (20, 20, 20) # black text/barcode
                    else:
                        pixels[y * w + x] = bg_color
                else:
                    # Sleek gradient / solid background
                    # Subtle vertical lighting on can sleeve
                    light = 1.0 + 0.15 * math.sin((x / 1195.0) * math.pi)
                    r = min(255, int(bg_color[0] * light))
                    g = min(255, int(bg_color[1] * light))
                    b = min(255, int(bg_color[2] * light))
                    pixels[y * w + x] = (r, g, b)
                    
    tmp_bmp = f"/tmp/tex_{os.path.basename(out_jpg)}.bmp"
    save_bmp(tmp_bmp, w, h, pixels)
    cmd = f"sips -s format jpeg -s formatOptions 92 {tmp_bmp} --out {out_jpg}"
    subprocess.run(cmd, shell=True, check=True)
    if os.path.exists(tmp_bmp): os.remove(tmp_bmp)
    print(f"Created texture: {out_jpg}")

def create_card(label_bmp, bg_tint, out_png):
    # Generate 512x512 transparent card with rounded preview
    w, h = 512, 512
    pixels = [(0, 0, 0, 0)] * (w * h)
    
    # We create an upright rounded bottle/can preview
    cw, ch = 320, 440
    cx0 = (w - cw) // 2
    cy0 = (h - ch) // 2
    
    radius = 50.0
    
    for y in range(h):
        for x in range(w):
            dx = max(0, cx0 + radius - x, x - (cx0 + cw - radius))
            dy = max(0, cy0 + radius - y, y - (cy0 + ch - radius))
            dist = math.sqrt(dx*dx + dy*dy)
            
            if cx0 <= x < cx0 + cw and cy0 <= y < cy0 + ch:
                if dist <= radius:
                    # Inside rounded rectangle
                    u = (x - cx0) / float(cw)
                    v = (y - cy0) / float(ch)
                    img_x = int(u * (label_bmp['w'] - 1))
                    img_y = int(v * (label_bmp['h'] - 1))
                    r, g, b = get_pixel(label_bmp, img_x, img_y)
                    
                    # Highlight reflection on left
                    shine = 0.3 * max(0.0, 1.0 - abs(u - 0.25) / 0.2)
                    r = min(255, int(r + shine * 255))
                    g = min(255, int(g + shine * 255))
                    b = min(255, int(b + shine * 255))
                    
                    # Smooth antialiased edge
                    edge_alpha = 1.0
                    if dist > radius - 1.5:
                        edge_alpha = max(0.0, min(1.0, (radius - dist) / 1.5))
                    pixels[y * w + x] = (r, g, b, int(255 * edge_alpha))
            
    tmp_bmp = f"/tmp/card_{os.path.basename(out_png)}.bmp"
    save_rgba_bmp(tmp_bmp, w, h, pixels)
    cmd = f"sips -s format png {tmp_bmp} --out {out_png}"
    subprocess.run(cmd, shell=True, check=True)
    if os.path.exists(tmp_bmp): os.remove(tmp_bmp)
    print(f"Created card: {out_png}")

def main():
    print("Reading reference assets...")
    green_bmp = read_bmp('/tmp/green.bmp')
    berry_bmp = read_bmp('/tmp/berry_ref.bmp')
    classic_bmp = read_bmp('/tmp/classic_ref.bmp')
    strong_bmp = read_bmp('/tmp/strong_ref.bmp')
    
    # 1. Textures
    # Berry Americano: Crimson red (#801625 = 128, 22, 37)
    create_texture(berry_bmp, green_bmp, (128, 22, 37), "BERRY AMERICANO", "assets/textures/texture-berry-americano.jpg")
    
    # Aren Latte Classic: Golden Caramel (#a5713c = 165, 113, 60)
    create_texture(classic_bmp, green_bmp, (165, 113, 60), "AREN LATTE CLASSIC", "assets/textures/texture-latte-classic.jpg")
    
    # Aren Latte Strong: Deep Roasted Espresso (#54250a = 84, 37, 10)
    create_texture(strong_bmp, green_bmp, (84, 37, 10), "AREN LATTE STRONG", "assets/textures/texture-latte-strong.jpg")
    
    # 2. Cards
    create_card(berry_bmp, (128, 22, 37), "assets/cards/card-berry-americano.png")
    create_card(classic_bmp, (165, 113, 60), "assets/cards/card-latte-classic.png")
    create_card(strong_bmp, (84, 37, 10), "assets/cards/card-latte-strong.png")
    
    print("All assets successfully built!")

if __name__ == '__main__':
    main()
