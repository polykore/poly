#~find

import os


def run(term, args):

    if not args:
        term.write("Usage: find <name>")
        return

    search = " ".join(args).lower()

    found = False

    for root, dirs, files in os.walk(term.cwd):

        #~search folders
        for folder in dirs:

            if search in folder.lower():

                path = os.path.join(root, folder)

                term.write(path)

                found = True

        #~search files
        for file in files:

            if search in file.lower():

                path = os.path.join(root, file)

                term.write(path)

                found = True

    if not found:

        term.write("No matches found.")