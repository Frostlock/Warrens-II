REM This script will create a packaged version of the project that can be easily distributed.
REM This is the Windows script.
REM There are two extra options
REM   --noconsole : This lets the application run without a console window
REM   --icon : Assigns an icon to the executable
REM
REM The script can package into a directory or into a file.
REM To package into a directory remove the --onefile parameter which can be useful for debugging.
REM
REM When changing parameters it is recommended to delete existing spec file and the build and dist directories.

python -m PyInstaller --clean --noconfirm --workpath=".\build" --specpath=".\build"  --distpath=".\..\..\dist" --add-data="..\..\..\src\WarrensClient\assets\*;WarrensClient\assets" --add-data="..\..\..\src\WarrensClient\music\*;WarrensClient\music" --add-data="..\..\..\src\WarrensClient\sfx\*;WarrensClient\sfx" --add-data="..\..\..\src\WarrensGame\*.csv;WarrensGame" --onefile --noconsole --icon=python.ico ..\..\src\Warrens.py

REM When working with a virtual environment you can run the above command through a pycharm task.
REM For this you can use a regular python run task, instead of pointing it to a script, point it to module PyInstaller.
REM commandline parameters to be included from --clean to the end of the line.

REM For additional compression you can use UPX (https://upx.github.io/)
REM add the --upx-dir parameter
REM For example: --upx-dir=C:\Users\pboogaer\Pycharm\Warrens-II\non_git\upx-3.95-win64\upx.exe
REM During testing on my Win 7 machine I didn't manage to get any additional compression using this.