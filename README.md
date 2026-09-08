# Better Quickslots

A Dawnwalker UI mod with thin, stock-style rarity borders for inventory, crafting, and gameplay quickslots, plus inventory quickslot hover details.

**Current release: v1.0.0 — first stable release.**

The installed mod files are identical to the confirmed v0.4.4 build. Existing v0.4.4 users do not need to reinstall.

## Install or upgrade

Download [BetterQuickslots v1.0.0](https://github.com/t0ddharris/Better-Quickslots/releases/download/v1.0.0/BetterQuickslots-v1.0.0.zip). Close the game and copy its three mod files into `<game folder>\Dawnwalker\Content\Paks\~mods`:

- `00000000_BetterQuickslots_P.pak`
- `00000000_BetterQuickslots_P.ucas`
- `00000000_BetterQuickslots_P.utoc`

When upgrading from the former Quickslot Hover mod, remove its three old mod files first or disable that version in your mod manager. The new filenames will not overwrite the old files. UE4SS is not required.

## Source and building

The repository includes the Python builders and the current installable ZIP. Original game assets, mappings, tool binaries, crash reports, and development archives are excluded.

See [Build instructions](docs/BUILD.md) for the required local inputs and validation process. A fresh clone requires those separately obtained inputs before it can rebuild the mod. See [Changelog](docs/CHANGELOG.md) for release notes.

## Behavior and compatibility

The thin border uses one visible copy of the original diamond artwork, with the outer black halo trimmed. Rarity colors update when items change, and empty slots have no rarity outline. Inventory hover, icons, counts, and the stock shared-button property layout are preserved.

Mods replacing the inventory hub or shared HUD quickslot button may conflict. Game updates may require a rebuild.
