import serial
import time
import threading

CMD_START = ""
CMD_END = "0D0A"
RESET_CMD = "ABE3"
VERSION_NUMBER_CMD = "ABCD"
READ_PARAMETERS_CMD = "AAE2"
READ_DEVICE_ID_CMD = "F2AD"

baud_rates = {
    1:1200,
    2:2400,
    3:4800,
    4:9600,
    5:19200,
    6:38400}

tx_power_levels = {
    0:-35, 
    1:-25, 
    2:-15,  
    3:-5,
    4:0,
    5:+3,
    6:+6,
    7:+9,
    8:+10,
    9:+12
}

mode_dict = {
    0xA0: "Transparent Transmission",
    0xC0: "Remote control transmitter (With LED indicator)",
    0xC1: "Remote control transmitter",
    0xC2: "Non learning remote control receiving or switch value receiving (IO level synchronization)",
    0xC3: "Non learning remote control receiving (Level reversal)",
    0xC4: "Non learning remote control receiving (Pulse level)",
    0xC5: "Learning remote control receiving (IO level synchronization)",
    0xC6: "Learning remote control receiving (Level reversal) Pulse level ",
    0xC7: "Learning remote control receiving (Pulse level)",
}


class Jdy41:

    def __init__(self, port, baudrate=9600, timeout=1.0):
        self.serial = serial.Serial(port, baudrate, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE, timeout=timeout)
        print(f'Serial {"open " if self.serial.isOpen() else "failed"}')
        self.serial.flush()

    def listen(self, filename="jdy41_data.txt", allowed_misses=1e9):
        self.is_listening = True
        consecutive_timeouts = 0

        with open(filename, "w") as f:

            while self.is_listening:
                data_in = self.serial.readline()
                if len(data_in) == 0:
                    consecutive_timeouts += 1
                    if consecutive_timeouts > allowed_misses:
                        print("No data for 10 consecutive timeouts")
                        break
                else:
                    consecutive_timeouts = 0

                    print(f"Data len: {len(data_in)}")
                    try:
                        str_in = data_in.decode('utf-8')
                        f.write(str_in)
                        print(f"{str_in}")
                    except:
                        print("Failed to get data")

    def send_cmd(self, cmd):
        if not self.serial.isOpen():
            print("Warning: Serial not open")
            return
        # print(f"Sending command {cmd}")
        num_written = self.serial.write(bytes.fromhex(CMD_START + cmd + CMD_END))
        time.sleep(0.1)
        return num_written

    def reset(self):
        if not self.serial.isOpen():
            print("Warning: Serial not open")
            return
        print("Resetting Jdy41")
        self.send_cmd(RESET_CMD)
        data = self.serial.read(5)
        try:
            str_in = data.decode('utf-8')
            if "+OK" in str_in:
                print(f"Reset successful: {str_in}")
        except:
            print("Warning: Reset failed")


    def get_version(self):
        if not self.serial.isOpen():
            print("Warning: Serial not open")
            return
        print("Getting version of Jdy41")
        self.send_cmd(VERSION_NUMBER_CMD)
        data = self.serial.read(5)
        try:
            str_in = data.decode('utf-8')
            print(f"Version: {str_in}")
        except:
            print("Warning:Failed to get version")

    def get_device_id(self):
        if not self.serial.isOpen():
            print("Serial not open")
            return
        print("Getting ID of Jdy41")
        self.send_cmd(READ_DEVICE_ID_CMD)
        data = self.serial.read(8)
        try:
            print(f"ID: {data[2:5].hex()}")
        except:
            print("Failed to get ID")

    def get_params(self):
        if not self.serial.isOpen():
            print("Serial not open")
            return
        print("Getting parameters of Jdy41")
        self.send_cmd(READ_PARAMETERS_CMD)
        data = self.serial.read(14)
        try:
            print(f"Parameters: {data.hex()}")
            buad_rate = data[2]
            channel = data[3]
            tx_power = data[4]
            mode = data[5]
            id = data[6:9]
            ack = data[10]
            print(f"Parameters:")
            print(f"  buad_rate {baud_rates[buad_rate]} ({buad_rate})")
            print(f"  channel {channel}")
            print(f"  tx_power {tx_power_levels[tx_power]}dB ({tx_power})")
            print(f"  mode {mode_dict.get(mode, 'Unknown')} ({hex(mode)})")
            print(f"  id 0x{id.hex()}")
            print(f"  ack {ack}")
        except:
            print("Failed to get Parameters")

    def close(self):
        self.is_listening = False
        self.serial.close()
        print(f'Serial {"closed " if not self.serial.isOpen() else "failed to close"}')

if __name__ == "__main__":
    print("Starting Jdy41 test")
    jdy41 = Jdy41("/dev/tty.usbserial-A50285BI")
    jdy41.listen()
    jdy41.close()
