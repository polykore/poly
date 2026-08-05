#~mv

import os
import shutil


def run(term, args):

    if len(args) != 2:
        term.write("Usage: mv source destination")
        return

    source = os.path.join(term.cwd, args[0])
    destination = os.path.join(term.cwd, args[1])

    if not os.path.exists(source):
        term.write("mv: source not found")
        return

    try:

        shutil.move(source, destination)

        term.write("Move complete.")

    except Exception as e:

        term.write(f"mv: {e}")