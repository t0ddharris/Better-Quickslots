# Changelog

## v1.0.0 Saturated

- Adds an optional, more pronounced rarity border using the same thin diamond artwork and geometry.
- Boosts only the retained border ring: color gain 1.45 and alpha gain 1.20. Preserves its transparent footprint, dark center, and all cooked mip levels.
- Retains rarity hues, the blue-rarity correction, empty-slot behavior, hover details, icons, counts, and layout. All five non-texture assets remain byte-identical to Default.
- Confirmed working by the user. Full static validation passed; the release preserves the approved mod payloads byte-for-byte.
- Default v1.0.0 mod binaries remain unchanged. Install either Default or Saturated and replace all three files together when switching.
- Adds `--variant saturated` and an optional `--output-root` to the builder. Both packaged READMEs and the future template omit legacy upgrade instructions and validation/source sections.

## v1.0.0

- First stable release, promoted from the confirmed v0.4.4 build.
- No visual or gameplay changes; the three installed files are byte-for-byte identical to v0.4.4.
- Updated release version, documentation, ZIP name and download links.
- Existing v0.4.4 installations need no update. Installed mod filenames remain unchanged.

## v0.4.4

- Thin, stock-style rarity borders across inventory, crafting, and gameplay quickslots.
- One visible trimmed diamond outline replaces the earlier five-layer bevel.
- Retains inventory hover details, item icons, stack counts, rarity colors, and the blue-rarity correction.
- Preserves the stock shared-button property layout to avoid the loading incompatibility encountered during development.
- Confirmed working in game.
- Project renamed to Better Quickslots. Installed filenames now use `00000000_BetterQuickslots_P`; remove the former mod's three files when upgrading.
