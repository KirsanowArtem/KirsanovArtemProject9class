import os

output_name = "SeaBattleApp2.exe"
python_file = "App2.py"

try:
    import PyInstaller
except ImportError:
    os.system("pip install pyinstaller")

os.system(f'pyinstaller --onefile --noconsole --log-level=DEBUG {python_file} --name "{output_name[:-4]}"')