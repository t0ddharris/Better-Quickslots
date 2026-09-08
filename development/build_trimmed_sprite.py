"""Trim only the outer alpha of a private copy of the game's rarity artwork."""
import base64
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UI = Path('Dawnwalker/Content/_Dawnwalker/UI/_Unified')
ATLAS = UI / 'HUD/Quickslots/Atlas/Textures/QSH_RarityAtlas_0.uasset'
SPRITE = UI / 'HUD/Quickslots/Atlas/Frames/T_Quickslot_RarityTrimmed.uasset'

def renamed(value, substitutions):
    if isinstance(value, str):
        for old, new in substitutions:
            value = value.replace(old, new)
        return value
    if isinstance(value, dict):
        return {k: renamed(v, substitutions) for k, v in value.items()}
    if isinstance(value, list):
        return [renamed(v, substitutions) for v in value]
    return value

def build():
    atlas = json.loads((ROOT / 'decoded/quickslot-atlas.json').read_text(encoding='utf-8-sig'))
    original = ROOT / 'extracted' / UI / 'HUD/Quickslots/Atlas/Textures/Atlas_0.ubulk'
    bulk = bytearray(original.read_bytes())
    texture = atlas['Exports'][0]
    extra = bytearray(base64.b64decode(texture['Extras']))
    # DataResource inline offsets are relative to the start of the export.
    prefix_size = texture['SerialSize'] - len(extra)
    assert prefix_size == 36
    width, height = 256, 512
    assert struct.unpack_from('<II', extra, 44) == (width, height)
    assert b'PF_B8G8R8A8\0' in extra[:80]

    # Original sprite: (1,235), 152x152. The bright diamond is at Manhattan
    # radii 61..66 around its center; the black halo extends to radius 76.
    mask = [1.0] * (width * height)
    for y in range(235, 387):
        for x in range(1, 153):
            radius = abs(x + 0.5 - 77.0) + abs(y + 0.5 - 311.0)
            mask[y * width + x] = max(0.0, min(1.0, 67.0 - radius))
    for mip, resource in enumerate(atlas['DataResources']):
        mip_width, mip_height = max(1, width >> mip), max(1, height >> mip)
        assert resource['SerialSize'] == mip_width * mip_height * 4
        external = bool(resource['LegacyBulkDataFlags'] & 0x100)
        target = bulk if external else extra
        offset = resource['SerialOffset'] - (0 if external else prefix_size)
        assert 0 <= offset <= len(target) - resource['SerialSize']
        # Average the full-resolution mask for every cooked mip, retaining
        # existing RGB and original mip filtering rather than repainting art.
        xstep, ystep = width // mip_width, height // mip_height
        for y in range(mip_height):
            for x in range(mip_width):
                coverage = sum(mask[sy * width + sx]
                               for sy in range(y * ystep, (y + 1) * ystep)
                               for sx in range(x * xstep, (x + 1) * xstep)) / (xstep * ystep)
                alpha = offset + (y * mip_width + x) * 4 + 3
                target[alpha] = round(target[alpha] * coverage)
    source = original.read_bytes()
    assert all(bulk[i] == source[i] for i in range(len(bulk)) if i % 4 != 3)
    assert any(bulk[i] != source[i] for i in range(3, len(bulk), 4))
    texture['Extras'] = base64.b64encode(extra).decode()
    old_path = '/Game/_Dawnwalker/UI/_Unified/HUD/Quickslots/Atlas/Textures/Atlas'
    new_path = old_path.rsplit('/', 1)[0] + '/QSH_RarityAtlas'
    atlas = renamed(atlas, [(old_path, new_path)])
    atlas['NameMap'] = ['QSH_RarityAtlas' if n == 'Atlas' else n for n in atlas['NameMap']]
    atlas['Exports'][0]['ObjectName'] = 'QSH_RarityAtlas_0'
    sprite = json.loads((ROOT / 'decoded/T_Quickslot_Background.json').read_text(encoding='utf-8-sig'))
    sprite = renamed(sprite, [('T_Quickslot_Background', 'T_Quickslot_RarityTrimmed'),
                              (old_path, new_path)])
    for imp in sprite['Imports']:
        if imp['ObjectName'] == 'Atlas_0':
            imp['ObjectName'] = 'QSH_RarityAtlas_0'
    sprite['NameMap'] = ['QSH_RarityAtlas' if n == 'Atlas' else n for n in sprite['NameMap']]
    outputs = []
    for asset, relative in ((atlas, ATLAS), (sprite, SPRITE)):
        from build_rarity import collect_names
        collect_names(asset)
        out = ROOT / 'extracted' / relative.with_suffix('.json')
        out.write_text(json.dumps(asset, indent=2), encoding='utf-8')
        outputs.append((out, relative))
    bulk_output = ROOT / 'extracted' / ATLAS.with_suffix('.ubulk')
    bulk_output.write_bytes(bulk)
    return outputs, bulk_output
