rem ツール名を指定する
set TOOL_NAME=vemt-unitypackage-validator
set ICON_PATH=%~dp0favicon.ico
set ADD_PATH=
rem -----------------------------------------------
rem 以下変更不要
rem -----------------------------------------------
set EXE_PATH=%~dp0exe
set TOOL_PATH=%~dp0src
cd %EXE_PATH%
rem pyinstallerを実行
pyinstaller %TOOL_PATH%\main.py  --hidden-import=PySide2.QtXml --onefile --clean --icon %ICON_PATH% -n %TOOL_NAME% -p %ADD_PATH%;%TOOL_PATH%
rem pyinstaller %TOOL_PATH%\main.py --onefile --clean --icon %ICON_PATH% -n %TOOL_NAME%
cd ..
mkdir %EXE_PATH%\dist\ui
xcopy ui\*.ui %EXE_PATH%\dist\ui