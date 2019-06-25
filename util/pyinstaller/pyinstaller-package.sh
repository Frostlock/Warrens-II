#!/usr/bin/env bash
# This script will create a packaged version of the project that can be easily distributed.
# This is the Linux script.
#
# The script can package into a directory or into a file.
# To package into a directory remove the --onefile parameter which can be useful for debugging.
#
# When changing parameters it is recommended to delete existing spec file and the build and dist directories.

pyinstaller --clean --noconfirm \
    --workpath="./build" \
    --specpath="./build" \
    --distpath="./../../dist" \
    --add-data="../../../src/WarrensClient/assets/*:WarrensClient/assets" \
    --add-data="../../../src/WarrensClient/music/*:WarrensClient/music" \
    --add-data="../../../src/WarrensClient/sfx/*:WarrensClient/sfx" \
    --add-data="../../../src/WarrensGame/*.csv:WarrensGame" \
    --onefile \
    ../../src/Warrens.py
