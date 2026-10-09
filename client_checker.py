import subprocess


class ClientChecker:

    @staticmethod
    def is_client_installed():

        try:

            result = subprocess.run(
                ["sc", "query", "GxCVD"],
                capture_output=True,
                text=True
            )

            output = result.stdout.upper()

            return (
                "RUNNING" in output
                or
                "STOPPED" in output
            )

        except:
            return False

    @staticmethod
    def get_status():

        if ClientChecker.is_client_installed():
            return "Installed"

        return "New Client"