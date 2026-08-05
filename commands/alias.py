#~alias

def run(term, args):

    if not args:

        if not term.aliases:

            term.write(
                "No aliases."
            )

            return


        for name, command in term.aliases.items():

            term.write(
                f"{name}='{command}'"
            )

        return


    text = " ".join(args)


    if "=" not in text:

        term.write(
            "Usage: alias name=\"command\""
        )

        return


    name, command = text.split(
        "=",
        1
    )


    command = command.strip(
        "\"'"
    )


    term.aliases[name] = command


    term.write(
        f"Alias created: {name} -> {command}"
    )