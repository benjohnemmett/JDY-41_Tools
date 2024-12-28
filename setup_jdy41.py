from jdy41 import Jdy41

print("Starting Jdy41 setup script")
jdy41 = Jdy41("/dev/tty.usbserial-A50285BI")

print("Resetting Jdy41...")
jdy41.reset()
print(f"Waiting on start message")

data_in = jdy41.serial.readline()
try:
    str_in = data_in.decode('utf-8')
    print(f"{str_in}")
except:
    print("Failed to get start message")

jdy41.get_version()
jdy41.get_params()
jdy41.get_device_id()

jdy41.close()