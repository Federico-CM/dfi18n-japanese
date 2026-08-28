#!/usr/bin/env bash

set -u

echo "========================================"
echo " DFI18n Japanese PoC - Quick Installer"
echo "========================================"
echo

# Directory containing this script.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

ENGINE_SRC="$SCRIPT_DIR/dfi18n"
DATA_SRC="$SCRIPT_DIR/dfi18n-data-ja"

# Known Linux Dwarf Fortress base-data directory.
DEFAULT_BASE="$HOME/.local/share/Bay 12 Games/Dwarf Fortress"
BASE="$DEFAULT_BASE"
MODS="$BASE/mods"

WARNINGS=0
ERRORS=0

warn() {
    echo "WARNING: $*"
    WARNINGS=$((WARNINGS + 1))
}

error() {
    echo "ERROR: $*" >&2
    ERRORS=$((ERRORS + 1))
}

ok() {
    echo "OK: $*"
}

echo "Package directory:"
echo "  $SCRIPT_DIR"
echo

echo "Checking package contents..."

check_source_file() {
    local path="$1"
    local description="$2"

    if [ -f "$path" ]; then
        ok "$description"
    else
        error "$description is missing:"
        echo "  $path"
    fi
}

check_source_file "$ENGINE_SRC/info.txt" \
    "DFI18n engine metadata"

check_source_file "$ENGINE_SRC/libs/libdfi18n.so" \
    "DFI18n native library"

check_source_file "$ENGINE_SRC/scripts_modinstalled/dfi18n.lua" \
    "DFI18n command script"

check_source_file "$DATA_SRC/info.txt" \
    "Japanese data-pack metadata"

check_source_file "$DATA_SRC/dfi18n-data/dfi18n.txt" \
    "Japanese data configuration"

check_source_file "$DATA_SRC/dfi18n-data/fonts/ja/NotoSansMonoCJKjp-Regular.otf" \
    "Japanese font"

check_source_file "$DATA_SRC/dfi18n-data/simple/ja.csv" \
    "Japanese dictionary"

echo

if [ "$ERRORS" -ne 0 ]; then
    echo "Installation aborted."
    echo
    echo "The package is incomplete. Fix the errors above and run"
    echo "quick_install.sh again."
    exit 1
fi

echo "Checking Dwarf Fortress location..."
echo "Expected DF base directory:"
echo "  $BASE"
echo

if [ ! -d "$BASE" ]; then
    error "Dwarf Fortress base directory was not found."
    echo
    echo "Expected:"
    echo "  $BASE"
    echo
    echo "If Dwarf Fortress uses another base directory, launch DF with"
    echo "DFHack and run:"
    echo
    echo "  :lua print(dfhack.filesystem.getBaseDir())"
    echo
    echo "Then install manually according to INSTALL.md."
    exit 1
fi

ok "Dwarf Fortress base directory exists"

if [ ! -d "$MODS" ]; then
    warn "mods directory does not exist; it will be created."
    mkdir -p "$MODS" || {
        error "Could not create:"
        echo "  $MODS"
        exit 1
    }
fi

ok "mods directory is available"

echo
echo "Checking for an existing DFI18n installation..."

if [ -e "$MODS/dfi18n" ]; then
    warn "Existing dfi18n directory found and will be replaced:"
    echo "  $MODS/dfi18n"
fi

if [ -e "$MODS/dfi18n-data-ja" ]; then
    warn "Existing dfi18n-data-ja directory found and will be replaced:"
    echo "  $MODS/dfi18n-data-ja"
fi

echo
echo "Installing..."

# Remove only the two directories managed by this package.
rm -rf "$MODS/dfi18n" "$MODS/dfi18n-data-ja" || {
    error "Could not remove an existing DFI18n installation."
    exit 1
}

cp -a "$ENGINE_SRC" "$MODS/dfi18n" || {
    error "Failed to install DFI18n engine."
    exit 1
}

cp -a "$DATA_SRC" "$MODS/dfi18n-data-ja" || {
    error "Failed to install Japanese data pack."
    exit 1
}

echo
echo "Verifying installed files..."

verify_file() {
    local path="$1"
    local description="$2"

    if [ -f "$path" ]; then
        ok "$description"
    else
        error "$description"
    fi
}

verify_file "$MODS/dfi18n/info.txt" \
    "engine metadata installed"

verify_file "$MODS/dfi18n/libs/libdfi18n.so" \
    "native library installed"

verify_file "$MODS/dfi18n/scripts_modinstalled/dfi18n.lua" \
    "command script installed"

verify_file "$MODS/dfi18n-data-ja/info.txt" \
    "Japanese data metadata installed"

verify_file "$MODS/dfi18n-data-ja/dfi18n-data/dfi18n.txt" \
    "Japanese data configuration installed"

verify_file "$MODS/dfi18n-data-ja/dfi18n-data/fonts/ja/NotoSansMonoCJKjp-Regular.otf" \
    "Japanese font installed"

verify_file "$MODS/dfi18n-data-ja/dfi18n-data/simple/ja.csv" \
    "Japanese dictionary installed"

echo

if [ "$ERRORS" -ne 0 ]; then
    echo "========================================"
    echo " INSTALLATION FAILED"
    echo "========================================"
    echo
    echo "One or more required files could not be installed."
    echo "See INSTALL.md for manual installation and troubleshooting."
    exit 1
fi

echo "========================================"
echo " INSTALLATION COMPLETE"
echo "========================================"
echo
echo "Installed to:"
echo "  $MODS"
echo
echo "Next:"
echo
echo "  1. Launch Dwarf Fortress with DFHack."
echo
echo "  2. In the DFHack console, run:"
echo
echo "       dfi18n enable"
echo
echo "  3. Check the Dwarf Fortress UI."
echo
echo "     The PoC should display:"
echo
echo "       Settings -> 設定"
echo
echo "If Japanese text does not appear, see INSTALL.md."
echo

if [ "$WARNINGS" -ne 0 ]; then
    echo "Installer completed with $WARNINGS warning(s)."
    echo "Review the messages above if something does not work."
fi
