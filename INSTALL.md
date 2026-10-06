# DFI18n Japanese Localization — Installation

## Quick Installation

1. Close Dwarf Fortress, then open a terminal in the directory containing this package and run:

   ```
   ./quick_install.sh
   ```

2. Launch Dwarf Fortress with DFHack.

3. In the DFHack console, run:

   ```
   dfi18n enable
   ```

4. Check the Dwarf Fortress interface.

For a quick installation check, look for this translated interface label:

```
Settings → 設定
```

If the game displays `設定`, the interface translation and Japanese rendering are working. You can also check supported item names on the embark screen or in a fortress.

If Japanese text does not appear, or if `quick_install.sh` reports an error or warning, continue with the detailed installation and troubleshooting information below.

---


# Detailed Installation and Troubleshooting

This package is an in-progress, partial Japanese localization for Dwarf Fortress using DFI18n.

Known working configuration:

- Dwarf Fortress 53.16
- DFHack 53.16-r1.1
- Linux x86-64
- Tested on Ubuntu 22.04

Current coverage includes Japanese material names and a growing set of item names, including furniture, containers, jewelry, bars, stones, logs, rough gems, cut gems, and large gems. The `Settings` interface label is also translated as `設定`.

Coverage varies by item type and material. Many other parts of the game still appear in English.

## Package contents

The package contains two mods:

    dfi18n/
    dfi18n-data-ja/

`dfi18n` is the DFI18n translation engine.

`dfi18n-data-ja` contains the Japanese font, simple translation dictionary, material vocabulary, and item-name translation rules.

The included `libdfi18n.so` is a Linux x86-64 native library built and tested for the configuration listed above.

## Requirements

A working installation of:

1. Dwarf Fortress 53.16
2. DFHack 53.16-r1.1

DFHack must be running with Dwarf Fortress.

## Important installation path

DFI18n must be installed into the Dwarf Fortress base-data `mods` directory used by DFHack.

For the standard Linux installation tested with this package, this is:

    ~/.local/share/Bay 12 Games/Dwarf Fortress/mods/

This is NOT necessarily the Steam directory containing the Dwarf Fortress executable and DFHack binaries.

If necessary, the correct base directory can be checked from the DFHack console with:

    :lua print(dfhack.filesystem.getBaseDir())

The `mods` directory is:

    <getBaseDir()>/mods/

## Clean installation

Close Dwarf Fortress before installing.

From the directory containing this `INSTALL.md`, define:

    PORTABLE="$(pwd)"
    BASE="$HOME/.local/share/Bay 12 Games/Dwarf Fortress"

Create the mods directory if necessary:

    mkdir -p "$BASE/mods"

For a clean installation, first verify whether old copies exist:

    ls -ld "$BASE/mods/dfi18n" "$BASE/mods/dfi18n-data-ja" 2>/dev/null

If old copies are present and you intentionally want to replace them, remove only these two directories:

    rm -rf "$BASE/mods/dfi18n"
    rm -rf "$BASE/mods/dfi18n-data-ja"

Then install the package:

    cp -a "$PORTABLE/dfi18n" "$BASE/mods/"
    cp -a "$PORTABLE/dfi18n-data-ja" "$BASE/mods/"

Do not install these mods under the Steam runtime directory merely because the Dwarf Fortress executable or DFHack binaries are located there.

## Verify installed files

Run:

    test -f "$BASE/mods/dfi18n/info.txt" && echo "OK engine info"
    test -f "$BASE/mods/dfi18n/libs/libdfi18n.so" && echo "OK native library"
    test -f "$BASE/mods/dfi18n/scripts_modinstalled/dfi18n.lua" && echo "OK command script"

    test -f "$BASE/mods/dfi18n-data-ja/info.txt" && echo "OK data info"
    test -f "$BASE/mods/dfi18n-data-ja/dfi18n-data/dfi18n.txt" && echo "OK data config"
    test -f "$BASE/mods/dfi18n-data-ja/dfi18n-data/fonts/ja/NotoSansMonoCJKjp-Regular.otf" && echo "OK Japanese font"
    test -f "$BASE/mods/dfi18n-data-ja/dfi18n-data/simple/ja.csv" && echo "OK Japanese dictionary"

    test -f "$BASE/mods/dfi18n-data-ja/dfi18n-data/rulesets/ja/items/index.toml" && echo "OK Japanese item rules"

All eight checks should print `OK`. These checks confirm that the listed files exist; check translation and rendering in game after enabling DFI18n.

## Enable DFI18n

Start Dwarf Fortress with DFHack.

In the DFHack console, run:

    dfi18n enable

On the known-working configuration this completes successfully.

## Verify the Japanese localization

Open the relevant Dwarf Fortress UI menu.

The simple dictionary includes this interface label:

    Settings → 設定

If the installation is working correctly, `Settings` should therefore appear as:

    設定

in the actual Dwarf Fortress interface.

Correct Japanese rendering in the Dwarf Fortress UI is the important test.

Also inspect supported item names on the embark screen or in a fortress. Examples checked with the translation tool and in game include:

    pig iron bars → 銑鉄の延べ棒
    rough rubies → ルビーの原石
    pear cut onyxes → ペアカットのオニキス

Some item types and material combinations remain untranslated.

The DFHack terminal itself may display Japanese text as mojibake even when translation and in-game rendering are working correctly.

For example, the translation test:

    dfi18n t Settings

may produce garbled terminal output instead of visibly displaying `設定`.

Do not use DFHack terminal mojibake alone as evidence that the Japanese font or translation is broken.

## Disable DFI18n

From the DFHack console:

    dfi18n disable

## Re-enable DFI18n

From the DFHack console:

    dfi18n enable

## Remove the localization

Close Dwarf Fortress.

Then remove only the two installed mod directories:

    BASE="$HOME/.local/share/Bay 12 Games/Dwarf Fortress"

    rm -rf "$BASE/mods/dfi18n"
    rm -rf "$BASE/mods/dfi18n-data-ja"

This does not remove the portable source/package directory.

## Japanese localization files

The Japanese simple dictionary for interface labels is:

    dfi18n-data-ja/dfi18n-data/simple/ja.csv

One example entry is:

    text,translation,tags
    Settings,設定,[ALIGNMENT:CENTER]

The Japanese translation rules are under:

    dfi18n-data-ja/dfi18n-data/rulesets/ja/

These include material vocabulary in `materials/`, item-name rules in `items/`, and gem names, cuts, and shapes in `gems/`.

The Japanese font is:

    dfi18n-data-ja/dfi18n-data/fonts/ja/NotoSansMonoCJKjp-Regular.otf

The Japanese data configuration is:

    dfi18n-data-ja/dfi18n-data/dfi18n.txt

and currently loads:

    [FONT:fonts]
    [DATA:simple:simple]
    [DATA:rulesets:rulesets]

## Compatibility

This package should currently be considered tested only with:

    Dwarf Fortress 53.16
    DFHack 53.16-r1.1
    Linux x86-64

The included native DFI18n library and hook compatibility have not been established for arbitrary Dwarf Fortress or DFHack versions.

Do not assume compatibility with another version without testing it first.
