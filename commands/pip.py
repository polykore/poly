#~pip

import subprocess
import sys


def run(term, args):

    if not args:

        args = [
            "--version"
        ]


    try:

        result = subprocess.run(

            [
                sys.executable,
                "-m",
                "pip"
            ] + args,


            capture_output=True,

            text=True

        )


        if result.stdout:

            term.write(
                result.stdout
            )


        if result.stderr:

            term.write(
                result.stderr
            )


    except Exception as e:

        term.write(
            str(e)
        )