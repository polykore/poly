#~newrun command

import os
import sys
import subprocess
import time
import shutil

COMPAT_MAP = {
    "xpsp3": "WINXPSP3",
    "winxpsp3": "WINXPSP3",
    "xpsp2": "WINXPSP2",
    "winxpsp2": "WINXPSP2",
    "win98": "WIN98",
    "98": "WIN98",
    "win95": "WIN95",
    "95": "WIN95",
    "win7": "WIN7RTM",
    "win7rtm": "WIN7RTM",
    "win8": "WIN8RTM",
    "vista": "VISTASP2"
}

def find_program(app, cwd):
    # check absolute or relative to cwd
    full_cwd_path = os.path.abspath(os.path.join(cwd, app))
    if os.path.exists(full_cwd_path):
        return full_cwd_path
    if not full_cwd_path.lower().endswith(".exe") and os.path.exists(full_cwd_path + ".exe"):
        return full_cwd_path + ".exe"

    if os.path.exists(app):
        return os.path.abspath(app)

    # check system PATH
    found = shutil.which(app)
    if found:
        return found

    if not app.lower().endswith(".exe"):
        found = shutil.which(app + ".exe")
        if found:
            return found

    return None

def run(term, args):
    if not args:
        term.write(
"""Usage:
  newRun <appname.exe> [-comp <version>] [-winamt <count>] [-time <seconds>]

Flags:
  -comp   compatibility mode (e.g. xpsp3, win98, win7)
  -winamt amount of app windows to open (e.g. 3)
  -time   auto-close app after specific time in seconds (e.g. 15)
""",
            False
        )
        return

    app = args[0]
    flags = args[1:]

    cwd = getattr(term, "cwd", os.getcwd())
    app_path = find_program(app, cwd)
    if not app_path:
        term.write(f"newRun: Cannot find executable '{app}'", False)
        return

    compatibility = None
    winamt = 1
    timeout_sec = None

    i = 0
    while i < len(flags):
        flag = flags[i].lower()
        if flag in ("-comp", "--comp"):
            if i + 1 < len(flags):
                val = flags[i + 1]
                compatibility = COMPAT_MAP.get(val.lower(), val.upper())
                i += 1
        elif flag in ("-winamt", "--winamt", "-win", "--win"):
            if i + 1 < len(flags):
                try:
                    winamt = int(flags[i + 1])
                except ValueError:
                    winamt = 1
                i += 1
        elif flag in ("-time", "--time", "-t", "--t"):
            if i + 1 < len(flags):
                try:
                    timeout_sec = float(flags[i + 1])
                except ValueError:
                    timeout_sec = None
                i += 1
        i += 1

    env = os.environ.copy()
    if compatibility:
        env["__COMPAT_LAYER"] = compatibility
        term.write(f"Compatibility mode set to: {compatibility}", False)

    spawned_processes = []
    for num in range(winamt):
        try:
            proc = subprocess.Popen([app_path], cwd=cwd, env=env)
            spawned_processes.append(proc)
            term.write(f"Started '{app_path}' (Instance {num + 1}/{winamt})", False)
        except Exception as e:
            term.write(f"Failed to launch '{app_path}': {e}", False)
        time.sleep(0.1)

    if timeout_sec and timeout_sec > 0 and spawned_processes:
        exe_name = os.path.basename(app_path)
        term.write(f"Timer set: Closing '{exe_name}' in {timeout_sec} second(s)...", False)

        # launch detached background timer process so it executes even after python exits
        ps_cmd = f"Start-Sleep -Seconds {int(timeout_sec)}; taskkill /F /IM '{exe_name}'; taskkill /F /IM '{app}'"
        try:
            subprocess.Popen(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_cmd],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
        except Exception as e:
            term.write(f"Failed to start timer process: {e}", False)
