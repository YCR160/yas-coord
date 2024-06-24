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
    width, height = right - left + 1, bottom - top + 1
    return {"_rect": {"Rect": {"top": top, "left": left, "width": width, "height": height}},
            "_pos": {"Pos": {"x": left, "y": top}},
            "_size": {"Size": {"width": width, "height": height}}}.get(suffix)

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

def blacken_and_restore_color(image_path, pos):
    """
    Blacken the image and restore the color in the position.

    Args:
        image_path (str): Path of the image.
        pos (dict): Dictionary containing the position.
    """
    img = Image.open(image_path)
    img_array = np.array(img)[:, :, :3]
    original_color = img_array[pos['y'], pos['x']].copy()
    img_array[:] = 0
    img_array[pos['y'], pos['x']] = original_color
    img = Image.fromarray(img_array)
    img.save(image_path)
    return original_color

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f)

data = load_json('rog.json')
combinations = list(product(data['game'], data['os'], data['resolutions']))
os_name_mapping = {'windows': 'Windows', 'macos': 'macOS', 'linux': 'Linux'}

for game, os_name, resolution in combinations:
    path = os.path.join('assets', game, os_name, resolution)
    if os.path.exists(path):
        json_dict = {file[:-4]: get_value(file[file.rfind('_'):-4], get_rectangle_coords(os.path.join(path, file)))
                     for file in os.listdir(path) if file.endswith('.png')}
        repo_file = os.path.join(path, game + '_repository_layout.json')
        if os.path.exists(repo_file):
            json_dict.update(load_json(repo_file))
        width, height = map(int, resolution.split('x'))
        save_dict = {'current_resolution': {'width': width, 'height': height},
                     'platform': os_name_mapping.get(os_name.lower(), os_name),
                     'ui': 'Mobile' if os_name == 'macos' else 'Desktop',
                     'data': {k: json_dict[k] for k in sorted(json_dict)}}
        if game == 'starrail':
            character_pos = save_dict['data']['starrail_relic_equipper_pos']['Pos']
            character_files = [file for file in os.listdir(os.path.join(path, 'characters')) if file.endswith('.png')]
            character_colors = {}
            for file in character_files:
                character_color = blacken_and_restore_color(os.path.join(path, 'characters', file), character_pos)
                character_colors[file[:-4]] = {'r': int(character_color[0]), 'g': int(character_color[1]), 'b': int(character_color[2])}
            print(character_colors)
        save_json(save_dict, os.path.join('target', game, os_name, os_name + resolution) + '.json')