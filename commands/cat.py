#~cat

import os


def run(term, args):

    if not args:
        term.write("Usage: cat <file>")
        return

    for filename in args:

        path = os.path.join(term.cwd, filename)

        if not os.path.exists(path):
            term.write(f"cat: '{filename}' not found")
            continue

        if os.path.isdir(path):
            term.write(f"cat: '{filename}' is a directory")
            continue

        try:

            with open(
                path,
                "r",
                encoding="utf8",
                errors="replace"
            ) as file:

                term.write(f"----- {filename} -----")

                for line in file:
                    term.write(line.rstrip())

        except Exception as e:

            term.write(f"cat: {e}")