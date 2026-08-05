#~which

import os


def run(term, args):

    if not args:
        term.write("Usage: which <command>")
        return

    command = args[0]

    #~check built-in command modules

    command_file = os.path.join(
        "commands",
        command + ".py"
    )

    if os.path.exists(command_file):

        term.write(
            os.path.abspath(command_file)
        )

        return


    #~check system PATH

    locations = os.environ.get(
        "PATH",
        ""
    ).split(os.pathsep)


    for folder in locations:

        path = os.path.join(
            folder,
            command
        )

        if os.path.exists(path):

            term.write(path)

            return


    term.write(
        f"{command}: not found"
    )