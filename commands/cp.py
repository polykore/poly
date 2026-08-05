#~cp

import os
import shutil


def run(term, args):

    recursive = False
    clean_args = []

    for arg in args:

        if arg == "-r":
            recursive = True
        else:
            clean_args.append(arg)

    if len(clean_args) != 2:
        term.write("Usage: cp [-r] source destination")
        return

    source = os.path.join(term.cwd, clean_args[0])
    destination = os.path.join(term.cwd, clean_args[1])

    if not os.path.exists(source):
        term.write("cp: source does not exist")
        return

    try:

        if os.path.isdir(source):

            if not recursive:
                term.write("cp: omitting directory (use -r)")
                return

            shutil.copytree(source, destination)

        else:

            shutil.copy2(source, destination)

        term.write("Copy complete.")

    except Exception as e:

        term.write(f"cp: {e}")