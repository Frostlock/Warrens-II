#!/usr/bin/env bash
# This script will create a packaged version of the project that can be easily distributed
#
# The script can package into a directory or into a file.
# To package into a directory remove the --onefile parameter which can be useful for debugging.
#
# When changing parameters it is recommended to delete existing spec file and the build and dist directories.

pyinstaller --clean --noconfirm \
    --workpath="./build" \
    --specpath="./build" \
    --distpath="./../../dist" \
    --add-data="../../../WarrensClient/assets/*:WarrensClient/assets" \
    --add-data="../../../WarrensClient/music/*:WarrensClient/music" \
    --add-data="../../../WarrensClient/sfx/*:WarrensClient/sfx" \
    --add-data="../../../WarrensGame/*.csv:WarrensGame" \
    --onefile \
    ../../Warrens.py
