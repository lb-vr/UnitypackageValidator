rem ツール名を指定する
set TOOL_NAME=vemt-unitypackage-validator
set ICON_PATH=%~dp0\favicon.ico
set ADD_PATH=
rem -----------------------------------------------
rem 以下変更不要
rem -----------------------------------------------
set EXE_PATH=%~dp0\exe
set TOOL_PATH=%~dp0\src
cd %EXE_PATH%
rem pyinstallerを実行
pyinstaller %TOOL_PATH%\main.py -w --onefile --clean --icon %ICON_PATH% -n %TOOL_NAME% -p %ADD_PATH%;%TOOL_PATH%
cd %~dp0