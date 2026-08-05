#~system tray

import pystray
from PIL import Image
import threading


class SystemTray:


    def __init__(self, terminal):

        self.terminal = terminal

        self.icon = None



    def start(self):

        image = Image.open(
            "logo.png"
        )


        menu = pystray.Menu(

            pystray.MenuItem(
                "Open Terminal",
                self.show
            ),

            pystray.MenuItem(
                "Exit",
                self.exit
            )

        )


        self.icon = pystray.Icon(

            "Python Terminal",

            image,

            "Python Terminal",

            menu

        )


        threading.Thread(

            target=self.icon.run,

            daemon=True

        ).start()



    def hide(self):

        self.terminal.root.withdraw()



    def show(self):

        self.terminal.root.deiconify()

        self.terminal.root.after(

            100,

            self.terminal.root.focus_force

        )



    def exit(self):

        if self.icon:

            self.icon.stop()


        self.terminal.root.destroy()