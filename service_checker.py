import subprocess

def get_service_status():

    try:

        result = subprocess.run(
            ["sc", "query", "GxCVD"],
            capture_output=True,
            text=True
        )

        output = result.stdout.upper()

        if "RUNNING" in output:
            return "RUNNING"

        if "STOPPED" in output:
            return "STOPPED"

        return "NOT FOUND"

    except Exception as error:

        return str(error)
