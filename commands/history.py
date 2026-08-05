#~history

def run(term, args):

    if not term.history:

        term.write(
            "No history."
        )

        return


    for number, command in enumerate(
        term.history,
        start=1
    ):

        term.write(
            f"{number}  {command}"
        )