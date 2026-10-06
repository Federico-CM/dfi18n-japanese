# Dwarf Fortress Japanese localization with DFI18n

An in-progress Japanese localization for Dwarf Fortress using [DFI18n](https://github.com/DFI18n/dfi18n). This repository packages the DFI18n engine and a Japanese data mod so the translations can be tested in game.

The localization is partial. It includes Japanese material names and a growing set of item names, including furniture, containers, jewelry, bars, stones, logs, rough gems, cut gems, and large gems. It also translates the **Settings** interface label. Many other parts of Dwarf Fortress still appear in English.

## Examples

| English item or label | Japanese |
| --- | --- |
| Settings | 設定 |
| pig iron bars | 銑鉄の延べ棒 |
| rough rubies | ルビーの原石 |
| pear cut onyxes | ペアカットのオニキス |

These examples have been checked with the translation tool and in game. Translation coverage varies by item type and material.

## Installation

The packaged Linux build has been tested with Dwarf Fortress 53.16, DFHack 53.16-r1.1, and Linux x86-64 (Ubuntu 22.04).

1. Close Dwarf Fortress.
2. From the repository directory, run:

   ```bash
   ./quick_install.sh
   ```

3. Launch Dwarf Fortress with DFHack.
4. In the DFHack console, run:

   ```text
   dfi18n enable
   ```

The installer uses the standard Linux Dwarf Fortress base-data `mods` directory. If your installation uses a different location, or the installer reports a problem, follow [INSTALL.md](INSTALL.md) for manual installation and troubleshooting.

If succesfully installed, the button **Settings** on will say **設定**. You can also inspect translated item names in the embark screen or in a fortress.

## Repository layout

- `dfi18n/` — bundled DFI18n engine mod and Linux native library.
- `dfi18n-data-ja/` — Japanese data mod, font, simple dictionary, and translation rules.
- `dfi18n-data-ja/dfi18n-data/rulesets/ja/materials/` — material vocabulary.
- `dfi18n-data-ja/dfi18n-data/rulesets/ja/items/` — item-name rules.
- `dfi18n-data-ja/dfi18n-data/rulesets/ja/gems/` — gem names, cuts, and shapes.
- `INSTALL.md` — detailed setup, verification, removal, and troubleshooting.

## Status and feedback

This is a work in progress, not a complete Japanese translation. Some item types and material combinations are still untranslated.

## Credits and licenses

DFI18n is developed by the [DFI18n project](https://github.com/DFI18n/dfi18n) and distributed under the MIT License. The bundled Noto Sans Mono CJK JP font is covered by the SIL Open Font License 1.1. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and the `licenses/` directory for provenance and license information.
