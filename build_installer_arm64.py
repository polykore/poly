import os
import sys
import subprocess
import shutil

def build_arm64_installer():
    print("Building Poly Terminal ARM64 Custom Setup Executable...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    installer_py = os.path.join(base_dir, "installer.py")
    arm64_build_dir = os.path.join(base_dir, "bin", "ARM64_Release")
    payload_dir = os.path.join(base_dir, "dist", "PolyTerminal_ARM64")

    if not os.path.exists(arm64_build_dir):
        print(f"Error: ARM64 build directory {arm64_build_dir} does not exist!")
        return

    # package ARM64 build into dist/PolyTerminal_ARM64
    shutil.rmtree(payload_dir, ignore_errors=True)
    shutil.copytree(arm64_build_dir, payload_dir)
    print(f"Copied ARM64 payload to {payload_dir}")

    logo_exe = os.path.join(base_dir, "logoExe.png")
    logo_png = os.path.join(base_dir, "logo.png")
    icon_file = os.path.join(base_dir, "app_icon.ico")

    # command line arguments for pyinstaller setup
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=PolyTerminalSetup_ARM64",
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
        print("\nARM64 installer build successful! Executable is located at 'dist/PolyTerminalSetup_ARM64.exe'.")
    else:
        print("\nARM64 installer build failed with exit code:", result.returncode)

if __name__ == "__main__":
    build_arm64_installer()
