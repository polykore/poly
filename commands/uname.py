#~uname

import platform


def run(term, args):

    if "-a" in args:

        info = (
            f"{platform.system()} "
            f"{platform.node()} "
            f"{platform.release()} "
            f"{platform.version()} "
            f"{platform.machine()}"
        )

        term.write(info)

    else:

        term.write(
            platform.system()
        )