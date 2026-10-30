# Better Quickslots — session guidance

## Project and user preferences

- Project: **Better Quickslots**, a UI mod for The Blood of Dawnwalker.
- **Current local packages: Default and Saturated v1.1.0 for Dawnwalker 1.1.** The user confirmed the Saturated compatibility test launches successfully; its exact payloads are retained in Saturated v1.1.0. Default uses the same compatibility changes with its original subtle texture treatment and still needs a separate in-game check. Current builders use isolated `development/patch11-stock` inputs. Preserve all older releases and baselines.
- Public repository: `https://github.com/t0ddharris/Better-Quickslots`.
- **v1.0.0 is the stable release, promoted from the confirmed v0.4.4 build with identical mod binaries.** v0.4.4 supplies the in-game visual and behavioral baseline until a changed build is explicitly confirmed.
- **Saturated v1.0.1 is the user-confirmed optional update**, using border color gain 2.0 and alpha gain 1.20. Its payloads are identical to the approved 2.0x test build. Saturated v1.0.0 (gain 1.45 / alpha 1.20) is already public on Nexus and must remain preserved, along with unchanged Default v1.0.0. Test labels are not public release versions.
- Keep the stock UI appearance: thin diamond rarity borders, original artwork, icons, counts, and layout. Avoid thick bevels, multiple visible outline layers, and black backgrounds extending beyond the colored edge.
- Preserve inventory hover details and rarity borders in inventory, crafting, and gameplay.
- Use `BetterQuickslots` in release and installed filenames; preserve the GitHub repository's actual hyphenated name in URLs.
- Keep the packaged `README.txt` concise: title/version, a brief release introduction, FEATURES, INSTALL / UPGRADE, UNINSTALL, and COMPATIBILITY. End after COMPATIBILITY. Omit validation/source sections, source/build/release-history links, and prior-build lineage wording unless the user requests them. Keep the builder's README template aligned with this format for future releases.
- Omit the legacy Quickslot Hover upgrade/removal paragraph from README files and future package templates. Keep the current Default/Saturated switching instructions.

## Public release documentation

- Write the repository README, packaged README, public changelog, and Nexus/GitHub release notes for players. Focus on features, visible changes, installation, upgrades, removal, compatibility, and limitations that affect use.
- Describe changes from the previous public release and use actual public version numbers. Internal test builds, tuning iterations, branch cleanup, and project maintenance with no player impact do not need public changelog entries.
- Keep debugging history, test results, approval conversations, asset hashes, payload comparisons, recooking details, and implementation parameters out of player documentation unless the user requests them or they directly help a player make a decision.
- Record internal experiments and testing in local-only `docs/DEVELOPMENT_HISTORY.md` or ignored notes under `development/`. Do not include those notes or diagnostic artifacts in public release packages or release notes. Keep necessary developer build instructions in `docs/BUILD.md`.
- Treat the user's documentation cuts as intentional editorial guidance. Do not restore removed internal detail in later releases. Keep generated README templates aligned with the approved concise documentation so rebuilding does not reintroduce it.

## GitHub and Git

- **Use GitHub CLI (`gh`) for GitHub work**, including repository inspection, authentication, issues, pull requests, and releases. Use Git for commits, fetches, and pushes. Do not default to the connector or browser for publishing.
- Prefer `gh` on PATH. A portable copy is available locally at `development/tools/github-cli/bin/gh.exe`.
- Check authentication and the target repository before writes. Expected account: `t0ddharris`. Never print or commit tokens.
- The connector previously returned `403 Resource not accessible by integration` for repository writes. CLI authentication succeeded. If authentication expires, start the normal device login and let the user authorize it.
- Check Git status, the staged file list, and `git diff --cached --check` before committing. Preserve unrelated user changes; do not force-push or rewrite published history without explicit authorization.
- For a Windows dubious-ownership error, use command-scoped `-c safe.directory=<verified workspace path>` when appropriate. Do not disable ownership checks globally.
- Publish when the user has authorized that work. A remote alone does not authorize publishing every local edit. Do not ask again when the current request already authorizes publication.
- Use a notes file with `gh release create`. Verify the repository, tag, published status, and uploaded ZIP SHA-256 against the local artifact.

## Workspace and publication scope

- `development/`: builders, local tools, original/decoded assets, diagnostics, staging, and verification baselines.
- `releases/`: current ZIP and unpacked installable files.
- `promo/`: active promotional images, banners, and screenshots. Keep these at the project root; do not archive them during release cleanup unless the user explicitly requests it.
- `archive/`: previous packages and diagnostic downloads.
- Read `docs/BUILD.md` for prerequisites and local inputs; update `docs/CHANGELOG.md` for releases.
- Local-only `docs/DEVELOPMENT_HISTORY.md` records past experiments. Its older status statements are historical.
- `.gitignore` intentionally uses an allowlist. Do not broaden it or force-add ignored development data.
- Publish reviewed source, documentation, and the intended release ZIP only. Exclude original/decoded game data, mappings, tools, reference containers, crash reports, probes, credentials, and personal machine data. The installable ZIP intentionally contains packaged mod assets.
- Preserve old baseline/reference folders during cleanup: several remain build dependencies. Read the build documentation before moving or deleting them.

## Build and validation

- Run `python development/build_all_ui.py` with Python 3.12, or locate an available Python runtime if it is not on PATH.
- Tested tools: UAssetGUI v1.1.0 and retoc v0.1.5, targeting UE5.5. The tools, Dawnwalker mapping, game inputs, and historical baselines are local prerequisites. A fresh clone alone cannot rebuild the release.
- Edit the Python builders, not generated JSON or packaged binaries. Keep original game inputs intact.
- The main builder imports the hover, rarity, and texture-trimming builders, packages six assets, re-extracts them, and verifies the result.
- For asset changes, run the complete pipeline: container integrity, recovered bytecode/properties/imports, texture mip bytes, stock consumer compatibility, and exactly one visible rarity outline.
- The local reference set lacks Paper2D's default sprite material. Only its two documented inherited import names have a narrow verification exception; do not broaden it to hide failures.
- Static checks do not prove in-game appearance or crash resolution. State what passed and what still needs user testing. Claim runtime confirmation only after an actual report or observation.
- Documentation-only changes do not require rebuilding. For a new asset release, update the version, output paths, README, changelog, download links, and ZIP allowlist together. Preserve the last confirmed release.

## Engine constraints learned during development

- Preserve the shared button's original `LoadedProperties` schema. Adding widget members to that class broke compatibility with existing cooked instance data and caused a loading crash.
- Shared rarity images are located through the existing `ItemBox` parent and child indices. Preserve widget ordering and the lookup relationship.
- Store the native `ItemRarityRow` result in an addressable local before using `EX_StructMemberContext`. Preserve the local's size and function flags. Reading directly from the struct-returning call previously caused an access violation.
- Recalculate bytecode sizes, context offsets, and jump targets when instructions change.
- The confirmed thin border renders only the innermost 1.19x trimmed diamond layer; four outer layers stay collapsed, including after opacity updates.
- Retain the private alpha-trimmed sprite/atlas and all cooked mip levels. The earlier rotated, sliced frame replacement produced broken-looking borders and was rejected.
- Preserve rarity colors, the blue-rarity correction, and empty-slot handling unless requested otherwise.

## Installed game and diagnostics

- Installed files: `00000000_BetterQuickslots_P.pak`, `.ucas`, and `.utoc`. Replace all three together. Upgrades from the former mod name must remove the old three files first.
- The mod does not require UE4SS. The user wants UE4SS left installed for other mods.
- `QuickslotRarityProbe` was removed from the game's UE4SS Mods folder after successful testing. Do not reinstall it unless needed for a new investigation and authorized by the task.
- Modify only this mod's explicitly identified installed files. Preserve UE4SS, other mods, saves, and settings. Resolve and validate exact paths before recursive moves or deletion.
