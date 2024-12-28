GNGGA_FIELDS = [
    "header",
    "time",
    "lat",
    "NS",
    "long",
    "EW",
    "quality",
    "numSV",
    "HDOP",
    "alt",
    "uAlt",
    "sep",
    "uSep",
    "diffAge",
    "diffStation"
]

NMEA_0183_START_CHAR = "$"
NMEA_0183_CHECKSUM_CHAR = "*"


GNGGA_LENGTH = len(GNGGA_FIELDS)

class GnggaEntry:
    def __init__(self, string):
        self.time = None
        self.lat = None
        self.lon = None
        self.alt = None

        if string[0] != NMEA_0183_START_CHAR:
            return
        string = string[1:]
        if NMEA_0183_CHECKSUM_CHAR not in string:
            return 
        
        data_cs_tokens = string.split(NMEA_0183_CHECKSUM_CHAR)
        if len(data_cs_tokens) != 2:
            return
        data_string = data_cs_tokens[0]
        data_bytes = data_string.encode('utf-8')
        calc_checksum = 0
        for byte in data_bytes:
            calc_checksum ^= byte

        if calc_checksum != int(data_cs_tokens[1], 16):
            print(f"Checksum fail: calculated {calc_checksum:02x} does not match received {data_cs_tokens[1]}")
            return

        data_tokens = data_string.split(',')

        if data_tokens[0] != "GNGGA":
            return

        if len(data_tokens) != GNGGA_LENGTH:
            print(f"Got {len(data_tokens)} tokens, expected {GNGGA_LENGTH}")
            return

        try:
            if len(data_tokens[1]) != 0:
                self.time = float(data_tokens[1])
            if len(data_tokens[2]) != 0 and len(data_tokens[3]) != 0:
                self.lat = float(data_tokens[2][0:2]) + float(data_tokens[2][2:])/60
                if data_tokens[3] == "S":
                    self.lat *= -1
            if len(data_tokens[4]) != 0 and len(data_tokens[5]) != 0:
                self.lon = float(data_tokens[4][0:3]) + float(data_tokens[4][3:])/60
                if data_tokens[5] == "W":
                    self.lon *= -1
            if len(data_tokens[9]) != 0:
                self.alt = float(data_tokens[9])
        except:
            print("Failed to parse GNGGA string")

    def is_valid(self):
        return \
            self.time is not None and \
            self.lat is not None and \
            self.lon is not None and \
            self.alt is not None

    def __str__(self):
        return f"{self.time} lat: {self.lat} lon:{self.lon} alt:{self.alt}"
