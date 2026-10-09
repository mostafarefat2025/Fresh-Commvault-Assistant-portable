import os
import subprocess

def open_console():

    paths = [

        r"C:\Program Files\Commvault\ContentStore\Base\cvlaunch.exe",

        r"C:\Program Files\Commvault ContentStore\Base\cvlaunch.exe"

    ]

    for path in paths:

        if os.path.exists(path):

            subprocess.Popen([path])

            return True

    return False