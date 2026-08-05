#~help ;cmd

import os


def run(term, args):

    commands_path = os.path.join(
        os.path.dirname(__file__)
    )

    commands = []

    for file in os.listdir(commands_path):

        if file.endswith(".py") and file != "__init__.py":

            commands.append(
                file[:-3]
            )

    commands.sort()


    if args:

        command = args[0]

        if command in commands:

            term.write(
                f"{command}: available command"
            )

            term.write(
                f"Module: commands/{command}.py"
            )

        else:

            term.write(
                f"No help available for {command}"
            )

        return


    term.write("""

 poly help: cmdlist


Available Commands:

""")


    for command in commands:

        term.write(
            f"  {command}"
        )


    term.write("""

Use:

help <command>

for command information.
""")