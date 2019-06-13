#!/usr/bin/env bash
pyinstaller -y --distpath ../dist onedir.spec

# Not working properly, needs a different spec file
#pyinstaller -y --onefile --distpath ../dist onefile.spec

# For some reason the data files are not added properly
#pyinstaller --noconfirm \
#    --add-data="../WarrensClient/assets/*:WarrensClient/assets" \
#    --add-data="../WarrensClient/music/*:WarrensClient/music" \
#    --add-data="../WarrensClient/sfx/*:WarrensClient/sfx" \
#    --add-data="../WarrensGame/*.csv:WarrensGame" \
#    ../Launcher.py
