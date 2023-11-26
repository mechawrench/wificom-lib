import os
import time
import version_info
import microcontroller

def run_settings(ui):
    print("Running settings")
    settingsMenuConfig = [("Info", displayInfo), ("Sound", soundSetting)]
    names = [name for (name, value) in settingsMenuConfig]
    values = [value for (name, value) in settingsMenuConfig]
    while True:
        settingValue = ui.menu(names, values, "")
        if settingValue == "":
            return
        while not ui.is_c_pressed():
            settingValue(ui)
        while ui.is_c_pressed():
            pass


def displayInfo(ui):
    print("Running displayInfo")
    infoText = [
        f"Version: {version_info.version}\nCP Ver: {os.uname().version.split()[0]}"
    ]
    index = 0
    while True:
        while not ui.is_c_pressed():
            ui.display_text(infoText[index % len(infoText)])
            if ui.is_a_pressed(False):
                index += 1
                time.sleep(0.15)
        ui.beep_cancel()
        while ui.is_c_pressed(True):
            return


def soundSetting(ui):
    print("Running soundSetting")
    settingsMenuConfig = [("Enable", True), ("Disable", False)]
    names = [name for (name, value) in settingsMenuConfig]
    values = [value for (name, value) in settingsMenuConfig]
    while True:
        result = ui.menu(names, values, "")
        if result == "":
            return
        while not ui.is_c_pressed():
            with open("config.py", 'r', encoding="utf-8") as f:
                oldSettings = f.read()
                newSettings = oldSettings.replace(f"config[\"sound_on\"] = {not result}\n",  f"config[\"sound_on\"] = {result}\n")
            with open("config.py", 'w', encoding="utf-8") as f:
                f.write(newSettings)
            ui.display_text("Saving...")
            time.sleep(0.5)
            microcontroller.reset()
        while ui.is_c_pressed():
            pass
