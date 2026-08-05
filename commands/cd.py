"""
#~cd


supports:

cd
cd ..
cd .
cd ~
cd -
cd folder
cd "Folder Name"
"""

import os


def run(term, args):

    #~save previous directory
    if not hasattr(term, "previous_cwd"):
        term.previous_cwd = term.cwd

    #~no arguments -> home
    if not args:
        new_path = os.path.expanduser("~")

    else:

        path = " ".join(args)

        if path == "~":
            new_path = os.path.expanduser("~")

        elif path == "-":
            new_path = getattr(term, "previous_cwd", term.cwd)

        elif path == ".":
            new_path = term.cwd

        elif path == "..":
            new_path = os.path.dirname(term.cwd)

        else:

            if os.path.isabs(path):
                new_path = path
            else:
                new_path = os.path.abspath(
                    os.path.join(term.cwd, path)
                )

    if not os.path.exists(new_path):
        term.write(f"cd: '{new_path}' does not exist")
        return

    if not os.path.isdir(new_path):
        term.write(f"cd: '{new_path}' is not a directory")
        return

    term.previous_cwd = term.cwd
    term.cwd = new_path