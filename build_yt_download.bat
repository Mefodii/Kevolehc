set venv_folder=kevolehc-venv
set project_folder=Kevolehc
start cmd.exe /k "..\%venv_folder%\Scripts\activate.bat & pyinstaller -F youtube\main\yt_download.py"