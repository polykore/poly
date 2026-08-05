#~grep

import os


def run(term, args):

    if len(args) < 2:
        term.write(
            "Usage: grep <text> <file>"
        )
        return


    search = args[0]

    filename = args[1]


    path = os.path.join(
        term.cwd,
        filename
    )


    if not os.path.exists(path):

        term.write(
            f"grep: {filename}: No such file"
        )

        return


    try:

        with open(
            path,
            "r",
            errors="ignore"
        ) as file:


            found = False


            for number, line in enumerate(
                file,
                1
            ):

                if search.lower() in line.lower():

                    term.write(
                        f"{number}: {line.rstrip()}"
                    )

                    found = True



            if not found:

                term.write(
                    "No matches found"
                )


    except Exception as e:

        term.write(
            str(e)
        )