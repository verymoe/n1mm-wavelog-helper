@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Finding SSL DLLs...
python find_dlls.py

echo Building executable...
pyinstaller --clean --onefile --name n1mm-wavelog-helper --console --add-data "config.json;." --add-binary "C:\Users\shiro\anaconda3\Library\bin\libssl-3-x64.dll;." --add-binary "C:\Users\shiro\anaconda3\Library\bin\libcrypto-3-x64.dll;." --add-binary "C:\Users\shiro\anaconda3\Library\bin\libmpdec-4.dll;." log_helper.py

echo Build complete! Executable is in dist\log-helper.exe
echo Copy config.json to the same directory as the exe before running.
pause