#!/usr/bin/env python3
"""
Procedural 3D Model Generator for ARN Coffee Thematic Floating Elements:
1. Roasted Arabica Coffee Bean (coffee-bean.glb)
2. Crystalline Rounded Ice Cube (ice-cube.glb)
3. Traditional Indonesian Gula Aren Batok / Palm Sugar Block (palm-sugar.glb)

Outputs clean, lightweight self-contained GLB files with vertex colors and PBR shading.
"""

import os
import trimesh
import numpy as np


def generate_coffee_bean(output_path: str):
    """Generates an organic roasted coffee bean with natural S-crease and curved back."""
    mesh = trimesh.creation.icosphere(subdivisions=4, radius=1.0)
    verts = mesh.vertices.copy()
    x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]

    # Proportions
    y = y * 1.42
    x = x * 0.82
    z = z * 0.58

    # Longitudinal banana curvature
    curve = 0.15 * (1.0 - np.clip(y / 1.42, -1, 1)**2)
    z = z + curve

    # Center S-curve crease & lips
    s_curve = 0.06 * np.sin(y * 2.2)
    dist = np.abs(x - s_curve)
    taper = np.clip(1.0 - (y / 1.35)**4, 0, 1)

    slit = 0.44 * np.exp(- (dist / 0.11)**2) * taper
    lip = 0.07 * np.exp(- ((dist - 0.17) / 0.10)**2) * taper

    front_mask = z > -0.05
    z[front_mask] = z[front_mask] - slit[front_mask] + lip[front_mask]

    # Subtle flatten on back
    back_mask = z < -0.3
    z[back_mask] = -0.3 + (z[back_mask] + 0.3) * 0.7

    verts[:, 0] = x
    verts[:, 1] = y
    verts[:, 2] = z
    mesh.vertices = verts

    # Vertex colors: Dark roast gradient + charred inner crease
    vertex_colors = np.zeros((len(verts), 4), dtype=np.uint8)
    for i in range(len(verts)):
        vx, vy, vz = verts[i]
        d = abs(vx - 0.06 * np.sin(vy * 2.2))
        if vz > 0 and d < 0.18:
            factor = d / 0.18
            r = int(28 + factor * 22)
            g = int(12 + factor * 14)
            b = int(5 + factor * 8)
        else:
            r = int(58 + (vy / 1.42) * 5)
            g = int(28 + (vy / 1.42) * 3)
            b = int(14)
        vertex_colors[i] = [r, g, b, 255]

    mesh.visual = trimesh.visual.ColorVisuals(vertex_colors=vertex_colors)
    mesh.fix_normals()

    glb = trimesh.exchange.gltf.export_glb(mesh)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(glb)
    print(f"Generated: {output_path} ({len(glb):,} bytes)")


def generate_ice_cube(output_path: str):
    """Generates a rounded superellipsoid ice cube with subtle melting surface variation."""
    mesh = trimesh.creation.icosphere(subdivisions=4, radius=1.0)
    verts = mesh.vertices.copy()

    p = 2.8
    v_sign = np.sign(verts)
    v_abs = np.abs(verts)
    verts_sq = v_sign * (v_abs ** (1.0 / p)) * 0.85

    noise = (0.02 * np.sin(verts_sq[:, 0] * 6.0) * np.cos(verts_sq[:, 1] * 6.0))[:, None]
    verts_sq += noise
    mesh.vertices = verts_sq

    # Vertex colors: Translucent cyan-white icy tint
    vertex_colors = np.zeros((len(verts_sq), 4), dtype=np.uint8)
    for i in range(len(verts_sq)):
        vy = verts_sq[i, 1]
        r = int(210 + vy * 20)
        g = int(235 + vy * 15)
        b = int(250)
        vertex_colors[i] = [min(255, max(0, r)), min(255, max(0, g)), b, 210]

    mesh.visual = trimesh.visual.ColorVisuals(vertex_colors=vertex_colors)
    mesh.fix_normals()

    glb = trimesh.exchange.gltf.export_glb(mesh)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(glb)
    print(f"Generated: {output_path} ({len(glb):,} bytes)")


def generate_palm_sugar(output_path: str):
    """Generates an Indonesian Gula Aren Batok (cylindrical puck with rounded edges)."""
    mesh = trimesh.creation.icosphere(subdivisions=4, radius=1.0)
    verts = mesh.vertices.copy()
    x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]

    r = np.sqrt(x**2 + z**2)
    r_safe = np.maximum(r, 1e-6)
    norm_x = x / r_safe
    norm_z = z / r_safe

    r_cyl = np.where(r > 0.3, 0.75 + 0.15 * (r - 0.3), r * 2.5)
    y_puck = np.tanh(y * 3.0) * 0.55

    verts[:, 0] = norm_x * r_cyl
    verts[:, 1] = y_puck
    verts[:, 2] = norm_z * r_cyl
    mesh.vertices = verts
    mesh.fix_normals()

    # Vertex colors: Two-tone caramel cut face and dark outer mold bark
    vertex_colors = np.zeros((len(verts), 4), dtype=np.uint8)
    for i in range(len(verts)):
        vy = verts[i, 1]
        if abs(vy) > 0.42:
            r_c, g_c, b_c = 112, 58, 22
        else:
            r_c, g_c, b_c = 78, 38, 14
        vertex_colors[i] = [r_c, g_c, b_c, 255]

    mesh.visual = trimesh.visual.ColorVisuals(vertex_colors=vertex_colors)

    glb = trimesh.exchange.gltf.export_glb(mesh)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(glb)
    print(f"Generated: {output_path} ({len(glb):,} bytes)")


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, 'assets', 'models')
    generate_coffee_bean(os.path.join(models_dir, 'coffee-bean.glb'))
    generate_ice_cube(os.path.join(models_dir, 'ice-cube.glb'))
    generate_palm_sugar(os.path.join(models_dir, 'palm-sugar.glb'))
