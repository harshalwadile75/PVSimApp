import re

def parse_pan_file(content):
    """
    Parse PAN file content (PV module specs).
    Returns: dict of key electrical values.
    """
    values = {}
    lines = content.decode("utf-8").splitlines()

    def find_val(keyword):
        for line in lines:
            if line.strip().startswith(keyword):
                parts = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if parts:
                    return float(parts[0])
        return None

    values["Pmax"] = find_val("Pmpp")
    values["Vmp"] = find_val("Vmpp")
    values["Imp"] = find_val("Impp")
    values["Voc"] = find_val("Voc")
    values["Isc"] = find_val("Isc")
    values["Efficiency"] = find_val("Effm")
    return values

def parse_ond_file(content):
    """
    Parse OND file content (Inverter specs).
    Returns: dict of basic values.
    """
    values = {}
    lines = content.decode("utf-8").splitlines()

    def find_val(keyword):
        for line in lines:
            if line.strip().startswith(keyword):
                parts = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if parts:
                    return float(parts[0])
        return None

    values["MaxACPower"] = find_val("PACMAX")
    values["Efficiency"] = find_val("EFFEURO")
    return values
