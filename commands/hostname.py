#~hostname



import socket


def run(term, args):

    term.write(
        socket.gethostname()
    )