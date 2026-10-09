from installer_engine import InstallerEngine

engine = InstallerEngine()

info = engine.get_client_information()

for key, value in info.items():
    print(f"{key}: {value}")