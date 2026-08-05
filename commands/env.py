#~env

import os


def run(term, args):

    for key, value in sorted(
        os.environ.items()
    ):

        term.write(
            f"{key}={value}"
        )