import re


pattern_code_postal = re.compile(r"^\d{5}$")

generic_pattern = re.compile(r"^[\w\sÀ-ÿ,\'\-\.@\(\)\+]*$")
