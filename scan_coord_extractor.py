from itertools import product
from math import gcd
import os
import json

import numpy as np
from PIL import Image

def get_value(suffix, rectangle_coords):
    """
    Get value based on suffix and rectangle coordinates.

    Args:
        suffix (str): Suffix, can be '_rect', '_pos' or '_size'.
        rectangle_coords (tuple): Rectangle coordinates, contains four integers.

    Returns:
        dict: Dictionary containing the position and size of the rectangle.
    """
    top, left, bottom, right = map(int, rectangle_coords)
    width, height = right - left, bottom - top
    return {"_rect": {"top": top, "left": left, "width": width, "height": height},
            "_pos": {"x": left, "y": top},
            "_size": {"width": width, "height": height}}.get(suffix)

def get_rectangle_coords(image_path):
    """
    Get the rectangle coordinates of the non-black area in the image.

    Args:
        image_path (str): Path of the image.

    Returns:
        tuple: A tuple containing four integers, representing the coordinates of the rectangle.
    """
    img_array = np.array(Image.open(image_path).convert('L'))
    non_black_coords = np.where(img_array != 0)
    return np.min(non_black_coords[0]), np.min(non_black_coords[1]), np.max(non_black_coords[0]), np.max(non_black_coords[1])

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f)

data = load_json('rog.json')
combinations = list(product(data['game'], data['os'], data['resolutions']))
os_name_mapping = {'windows': 'Windows', 'macos': 'MacOS', 'linux': 'Linux'}

for game, os_name, resolution in combinations:
    path = os.path.join('assets', game, os_name, resolution)
    if os.path.exists(path):
        json_dict = {file[:-4]: get_value(file[file.rfind('_'):-4], get_rectangle_coords(os.path.join(path, file)))
                     for file in os.listdir(path) if file.endswith('.png')}
        repo_file = os.path.join(path, game + '_repository_layout.json')
        if os.path.exists(repo_file):
            json_dict.update(load_json(repo_file))
        width, height = map(int, resolution.split('x'))
        g = gcd(width, height)
        resolution_family = f'{os_name_mapping.get(os_name.lower(), os_name)}{width // g}x{height // g}'
        save_dict = {'current_resolution': {'width': str(width), 'height': str(height)},
                     'resolution_family': resolution_family,
                     'data': {k: json_dict[k] for k in sorted(json_dict)}}
        save_json(save_dict, os.path.join('target', game, os_name, resolution) + '.json')