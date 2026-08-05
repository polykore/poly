#~tree

import os


def run(term, args):


    def show(path, prefix=""):

        try:

            items = sorted(
                os.listdir(path)
            )

        except:

            return


        for index, item in enumerate(items):

            full = os.path.join(
                path,
                item
            )

            last = index == len(items) - 1


            if last:

                branch = "└── "

            else:

                branch = "├── "


            term.write(
                prefix + branch + item
            )


            if os.path.isdir(full):

                if last:

                    new_prefix = prefix + "    "

                else:

                    new_prefix = prefix + "│   "


                show(
                    full,
                    new_prefix
                )


    term.write(
        os.path.basename(term.cwd)
    )

    show(term.cwd)