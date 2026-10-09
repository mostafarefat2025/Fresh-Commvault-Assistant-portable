def detect_group(ip):

    if ip.startswith("10.5."):
        return "Obour Workstations"

    if ip.startswith("10.6."):
        return "Borg Workstations"

    if ip.startswith("10.7."):
        return "Beni Suef Workstations"

    return "Default Group"