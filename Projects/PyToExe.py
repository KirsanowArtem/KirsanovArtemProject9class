import os

output_name = "SeaBattleApp.exe"
python_file = "App.py"

try:
    import PyInstaller
except ImportError:
    os.system("pip install pyinstaller")

os.system(f'pyinstaller --onefile  --log-level=DEBUG {python_file} --name "{output_name[:-4]}"')
