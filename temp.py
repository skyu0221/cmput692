import numeral

try:
    numeral.roman2int("asjbfah")
except ValueError as e:
    if str(e) == "Input contains invalid characters":
        print("error")
