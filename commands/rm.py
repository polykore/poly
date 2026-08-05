#~rm

import os
import shutil


def run(term, args):

    recursive = False
    force = False
    targets = []

    for arg in args:

        if arg.startswith("-"):

            if "r" in arg:
                recursive = True

            if "f" in arg:
                force = True

        else:

            targets.append(arg)

    if not targets:
        term.write("Usage: rm file")
        return

    for target in targets:

        path = os.path.join(term.cwd, target)

        if not os.path.exists(path):

            if not force:
                term.write(f"rm: '{target}' not found")

            continue

        try:

            if os.path.isdir(path):

                if recursive:

                    shutil.rmtree(path)

                else:

                    term.write(
                        f"rm: '{target}' is a directory (use -r)"
                    )

            else:

                os.remove(path)

            term.write(f"Deleted {target}")

        except Exception as e:

            term.write(f"rm: {e}")