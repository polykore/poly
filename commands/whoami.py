#~whoami

import getpass


def run(term, args):

    term.write(
        getpass.getuser()
    )