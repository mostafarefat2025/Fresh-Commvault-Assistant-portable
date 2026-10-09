def get_group(ip):

    if ip.startswith("10.5."):
        return "Obour Workstations"

    elif ip.startswith("10.6."):
        return "Borg Workstations"

    elif ip.startswith("10.7."):
        return "Beni Suef Workstations"

    return "Default Group"