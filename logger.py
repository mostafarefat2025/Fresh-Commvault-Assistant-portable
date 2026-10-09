from datetime import datetime

def write_log(message):

    with open(
        "install.log",
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"{datetime.now()} - {message}\n"
        )