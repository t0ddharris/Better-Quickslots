# Better Quickslots

Thin, stock-style item rarity borders for inventory, crafting, and gameplay quickslots, plus inventory quickslot hover details.

**v1.1.0 — updated for Dawnwalker 1.1.** Choose one version:

- [Default](releases/BetterQuickslots-v1.1.0.zip): the original, subtle rarity borders.
- [Saturated](releases/BetterQuickslots-v1.1.0-Saturated.zip): the same thin diamond artwork with stronger border color and opacity.

Both preserve rarity colors, icons, stack counts, layout, and inventory hover details. Empty slots have no rarity outline.

## Install or upgrade

Close the game. Extract your chosen ZIP and copy these three files into `<game folder>\Dawnwalker\Content\Paks\~mods`:

- `00000000_BetterQuickslots_P.pak`
- `00000000_BetterQuickslots_P.ucas`
- `00000000_BetterQuickslots_P.utoc`

Create `~mods` if needed. Replace all three files together when upgrading. Install either Default or Saturated, never both. To switch, replace all three files together or disable the other variant in your mod manager.

UE4SS is not required.

## Uninstall

Remove only the three Better Quickslots files listed above. UE4SS and other mods can stay installed.

## Compatibility

For Dawnwalker 1.1. Mods replacing the inventory hub or shared HUD quickslot button may conflict. Later game updates may require a rebuild.

## Source and building

See [Build instructions](docs/BUILD.md) for local prerequisites and [Changelog](docs/CHANGELOG.md) for release notes. Original game assets, mappings, tools, and diagnostic files are not included in the repository.
