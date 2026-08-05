#~touch

import os
import time


def run(term, args):

    if not args:
        term.write("Usage: touch <file>")
        return

    for filename in args:

        path = os.path.join(term.cwd, filename)

        try:

            if not os.path.exists(path):

                open(path, "w", encoding="utf8").close()

                term.write(f"Created {filename}")

            else:

                os.utime(path, None)

                term.write(f"Updated timestamp: {filename}")

        except Exception as e:

            term.write(f"touch: {e}")