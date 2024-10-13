import re


pattern_code_postal = re.compile(r"^\d{5}$")

generic_pattern = re.compile(r"^[A-Za-zÀ-ÿ'’,\s:0-9]*$")
