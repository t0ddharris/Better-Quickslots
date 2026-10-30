# Building Better Quickslots

Current version: **v1.1.0**, Default and Saturated, targeting **Dawnwalker 1.1**. Original game assets, mappings, tool binaries, crash dumps, and diagnostic outputs are local prerequisites and are not committed. A fresh clone alone cannot rebuild the mod.

## Requirements

- Python 3.12, or a compatible available Python runtime.
- Stock Dawnwalker 1.1 game files.
- UAssetGUI v1.1.0 at `development/tools/UAssetGUI.exe`, with the Dawnwalker mapping under `development/tools/Data/Mappings`.
- retoc v0.1.5 at `development/tools/retoc/retoc.exe`, targeting UE5.5.

## Current local inputs

The builder defaults to `development/patch11-stock`. Use `--input-root` to select another directory containing the same layout:

- `decoded/`: stock 1.1 `hub.json`, `button.json`, `fill.json`, `quickslots.json`, `gameplay-quickslots.json`, `quickslot-atlas.json`, and `T_Quickslot_Background.json`.
- `extracted/Dawnwalker/Content/`: corresponding stock assets and dependencies at their game-relative paths, including all quickslot atlas mip data.
- `verify-v02-containers/`: current `global.utoc`/`.ucas` and reference containers. The directory name is historical; these isolated references use the current game's UI dependencies and global container.

Extract stock files from a container-only directory that excludes installed mods; retoc can otherwise include mod overrides. The builder does not extract inputs automatically. Keep original inputs and historical baseline directories intact.

## Build

```powershell
python development/build_all_ui.py
python development/build_all_ui.py --variant saturated
```

Outputs:

- `releases/BetterQuickslots-v1.1.0.zip`
- `releases/BetterQuickslots-v1.1.0-Saturated.zip`
- Matching unpacked folders containing the three installable files and README.

Use `--output-root development/patch11-stock/regression` for a build that does not overwrite releases. Add `--test-build` to label an unconfirmed compatibility test. Both variants install the same filenames; only one can be installed at a time.

Default retains border gain 1.0 and alpha gain 1.0. Saturated retains the approved gain 2.0 and alpha gain 1.20. The existing trim, single 1.19x diamond layer, rarity tint logic, and empty-slot handling are shared.

## Validation and promotion

The builder packages six assets and re-extracts them to check container integrity, imports, function bytecode, properties, and texture mip bytes. It checks current stock consumer compatibility, the exact stock shared-button schema, preservation of every original 1.1 button function, one visible rarity outline, and ZIP CRC/content integrity. Compiled private Blueprint dependencies are also placed beside generated source JSON so UAssetAPI can resolve their schemas.

Only the two documented inherited Paper2D default material imports have a narrow recovery exception. Do not broaden it to mask other failures.

The user confirmed the Saturated 1.1 compatibility test launches successfully. Saturated v1.1.0 preserves those exact three payloads from `development/patch11-stock/dist/BetterQuickslots-Patch11-Test-Saturated`; only its package documentation and version label change. Default is rebuilt with the same compatibility changes and its original texture treatment. Static checks do not establish in-game appearance; Default still needs a separate in-game check.

## Preserved historical inputs

Keep `development/decoded`, `development/extracted`, `verify-v02-containers`, `staging-v02`, `verify-v041`, `staging-v044`, and the approved Saturated test/reference folders. They support historical audits and prior release reproduction. Current builds use the isolated 1.1 inputs instead of replacing these baselines.

Default v1.0.0 and Saturated v1.0.1 remain in releases; older archived packages remain preserved. They target the earlier game build. Internal experiments and detailed validation history belong in local-only `docs/DEVELOPMENT_HISTORY.md` or `development/` notes.
