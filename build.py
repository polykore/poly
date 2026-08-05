import os
import sys
import subprocess

def build():
    print("Building Poly Terminal with PyInstaller...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(base_dir, "main.py")
    commands_dir = os.path.join(base_dir, "commands")
    logo_file = os.path.join(base_dir, "logo.png")

    # command line arguments for pyinstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=PolyTerminal",
        f"--add-data={commands_dir};commands",
    ]

    if os.path.exists(logo_file):
        cmd.append(f"--add-data={logo_file};.")

    cmd.append(main_py)

    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\nBuild successful! Executable is located in the 'dist/PolyTerminal' directory.")
    else:
        print("\nBuild failed with exit code:", result.returncode)

if __name__ == "__main__":
    build()
