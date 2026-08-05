#~sudo command

import os
import sys
import ctypes
import subprocess
from ctypes import wintypes

LOGON32_LOGON_INTERACTIVE = 2
LOGON32_PROVIDER_DEFAULT = 0

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def authenticate_windows_user(username, password):
    advapi32 = ctypes.windll.advapi32
    token = wintypes.HANDLE()
    domain = os.environ.get("USERDOMAIN", ".")

    success = advapi32.LogonUserW(
        username,
        domain,
        password,
        LOGON32_LOGON_INTERACTIVE,
        LOGON32_PROVIDER_DEFAULT,
        ctypes.byref(token)
    )

    if success:
        ctypes.windll.kernel32.CloseHandle(token)
        return True
    return False

def run(term, args):
    if not args:
        term.write("Usage: sudo <command> [args...]")
        return

    cmd = " ".join(args)
    cwd = getattr(term, "cwd", os.getcwd())

    # if already running elevated as administrator, execute command directly and capture output (like 99% sure dis works but idk not a py expert) - code written by c/polykore
    if is_admin():
        term.write(f"[sudo] running elevated: {cmd}")
        try:
            proc = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
            if proc.stdout:
                term.write(proc.stdout, False)
            if proc.stderr:
                term.write(proc.stderr, False)
        except Exception as e:
            term.write(f"sudo error: {e}")
        return

    username = os.environ.get("USERNAME", "User")
    password = os.environ.get("SUDO_PASSWORD", "")

    if not password:
        term.write("sudo: no password provided.")
        return

    # verify password with windows lsa api
    if not authenticate_windows_user(username, password):
        term.write("sudo: 3 incorrect password attempts or authentication failed.")
        return

    term.write(f"[sudo] authentication successful. executing: {cmd}")

    # launch elevated command with windows uac runas
    ps_cmd = f"Start-Process cmd.exe -ArgumentList '/c {cmd}' -Verb RunAs -WorkingDirectory '{cwd}'"
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)
    except Exception as e:
        term.write(f"sudo execution error: {e}")