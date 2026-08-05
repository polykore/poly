import os
import sys
import subprocess

def build_installer():
    print("Building Single-File Poly Terminal Custom Setup Executable...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    installer_py = os.path.join(base_dir, "installer.py")
    payload_dir = os.path.join(base_dir, "dist", "PolyTerminal")
    logo_exe = os.path.join(base_dir, "logoExe.png")
    logo_png = os.path.join(base_dir, "logo.png")
    icon_file = os.path.join(base_dir, "app_icon.ico")

    if not os.path.exists(payload_dir):
        print(f"Error: Payload directory {payload_dir} does not exist!")
        return

    # command line arguments for pyinstaller setup
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=PolyTerminalSetup",
        f"--add-data={payload_dir};dist/PolyTerminal",
    ]

    if os.path.exists(logo_exe):
        cmd.append(f"--add-data={logo_exe};.")
    if os.path.exists(logo_png):
        cmd.append(f"--add-data={logo_png};.")
    if os.path.exists(icon_file):
        cmd.append(f"--icon={icon_file}")
        cmd.append(f"--add-data={icon_file};.")

    cmd.append(installer_py)

    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\nSingle-file installer build successful! Executable is located at 'dist/PolyTerminalSetup.exe'.")
    else:
        print("\nInstaller build failed with exit code:", result.returncode)

if __name__ == "__main__":
    build_installer()
