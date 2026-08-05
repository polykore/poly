#~settings

import json
import os


SETTINGS_FILE = "terminal_settings.json"


DEFAULT_SETTINGS = {

    "background": "#050505",

    "foreground": "#ffffff",

    "cursor": "#58a6ff",

    "font": "Cascadia Mono",

    "font_size": 12,

    "slow_type": True,

    "typing_speed": 0.01

}



def load_settings():

    #~ if settings file does not exist;
    #~ create it with defaults

    if not os.path.exists(SETTINGS_FILE):

        save_settings(DEFAULT_SETTINGS)

        return DEFAULT_SETTINGS.copy()



    try:

        with open(
            SETTINGS_FILE,
            "r"
        ) as file:

            settings = json.load(file)



        #~ add missing settings automatically

        for key, value in DEFAULT_SETTINGS.items():

            if key not in settings:

                settings[key] = value



        return settings



    except Exception:

        return DEFAULT_SETTINGS.copy()



def save_settings(settings):

    with open(
        SETTINGS_FILE,
        "w"
    ) as file:

        json.dump(

            settings,

            file,

            indent=4

        )