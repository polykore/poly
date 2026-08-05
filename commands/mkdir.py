#~mkdir

import os


def run(term, args):

    if not args:
        term.write("Usage: mkdir <folder>")
        return

    create_parents = False
    folders = []

    for arg in args:

        if arg == "-p":
            create_parents = True

        else:
            folders.append(arg)

    if not folders:
        term.write("mkdir: missing directory name")
        return

    for folder in folders:

        path = os.path.join(term.cwd, folder)

        try:

            if create_parents:
                os.makedirs(path, exist_ok=True)
            else:
                os.mkdir(path)

            term.write(f"Created directory: {folder}")

        except FileExistsError:

            term.write(f"mkdir: '{folder}' already exists")

        except Exception as e:

            term.write(f"mkdir: {e}") 