# Building Better Quickslots

The repository contains the mod's Python builders and the current installable ZIP. Original game assets, decoded game data, game mappings, tool binaries, crash dumps, and local diagnostic outputs are not committed.

## Requirements

- Windows and Python 3.12 (the tested environment).
- A local installation of The Blood of Dawnwalker matching the source assets.
- [UAssetGUI](https://github.com/atenfyr/UAssetGUI) v1.1.0, with the Dawnwalker mapping configured under `development/tools/Data/Mappings`.
- [retoc](https://github.com/trumank/retoc) v0.1.5 under `development/tools/retoc`.

The asset format used by the builders is UE5.5. Build-time mappings and reference assets must be obtained separately; a fresh Git clone alone cannot rebuild the release.

## Local input layout

Paths are relative to `development/`:

- `tools/UAssetGUI.exe` and `tools/retoc/retoc.exe`: conversion tools.
- `decoded/`: original decoded JSON, including `hub.json`, `button.json`, `fill.json`, `quickslots.json`, `gameplay-quickslots.json`, `quickslot-atlas.json`, and `T_Quickslot_Background.json`.
- `extracted/Dawnwalker/Content/`: original assets and dependencies at their game-relative paths, including the quickslot atlas bulk data.
- `verify-v02-containers/`: local reference containers (`global` and `references`) used to recover import names.
- `staging-v02/`: original inventory layout and hover assets used as byte-for-byte regression baselines.
- `verify-v041/`: decoded v0.4.1 button assets used to check unchanged bytecode and class schemas.
- `staging-v044/`: confirmed v0.4.4 assets, also used by v1.0.0, for byte-for-byte comparisons of every non-texture asset.

These are the inputs retained in the development workspace. The scripts do not extract them automatically from a game installation.

## Run

```powershell
python development/build_all_ui.py
```

Build the optional Saturated package separately:

```powershell
python development/build_all_ui.py --variant saturated
```

This writes `releases/BetterQuickslots-v1.0.0-Saturated.zip` and an unpacked folder with the same name. Default remains v1.0.0. Both packages install the same three filenames; install only one variant at a time. Each variant has separate staging and verification folders.

For a default regression build without overwriting the preserved release:

```powershell
python development/build_all_ui.py --output-root development/saturated-audit/default-regression
```

The Saturated treatment multiplies the existing retained border's RGB intensity by 1.45 and its trimmed alpha by 1.20, clamped to the texture's byte range. It uses the same artwork and rarity tint logic, preserving rarity hues while lifting border tone and opacity. The adjustment is limited to the existing border ring (Manhattan radii 60 through 66), leaving the dark center and transparent footprint intact. Mask coverage weights the adjustment in every original cooked mip. Default gain values remain 1.0.

The builder regenerates the inventory hover patch, applies the rarity border, trims a private copy of the texture's outer alpha, creates the shared button with the stock property layout, then packages six assets. It writes `releases/BetterQuickslots-v1.0.0.zip` and the unpacked files beside it.

Validation additionally checks that all five non-texture assets match the confirmed v0.4.4/v1.0.0 staging files byte-for-byte, that tone adjustments preserve the default alpha footprint at every mip, and that the ZIP passes CRC checks with exactly the intended files.

Validation covers container integrity, recovered Blueprint functions and properties, texture mip bytes, compatibility with stock HUD/crafting templates, and exactly one visible rarity outline. The local reference set does not include Paper2D's stock default sprite material, so its two inherited import names cannot be recovered locally; they are retained from the source sprite.

In-game testing remains necessary after changing assets or supporting a new game patch.

## Stable release promotion

v1.0.0 promotes the confirmed v0.4.4 build without recooking its assets. Only the ZIP name and enclosed documentation changed; all three installed files are byte-for-byte identical. The builder now targets v1.0.0 for future rebuilds. The v0.4.4 ZIP and GitHub release are preserved.

## Saturated v1.0.0 promotion

The user confirmed the final Saturated treatment (color gain 1.45, alpha gain 1.20) and selected v1.0.0 as its release version. The three mod payloads are copied unchanged from the approved candidate; promotion changes only the version label and package documentation. Default v1.0.0 remains unchanged.

Earlier test packages are retained locally under `archive/saturated-candidates/`. The final candidate's staging and verification inputs remain under `development/staging-v101-saturated/` and `development/verify-v101-saturated/`. Future Saturated builds use separate `v100-saturated-release` staging and verification folders. Container packing can differ between builds; preserve the promoted payloads when only changing release documentation.
