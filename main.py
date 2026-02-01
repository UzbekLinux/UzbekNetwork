#!/usr/bin/python3
import os
import subprocess

def command(command):
    if command == "ping":
        return "pong"
    elif command == "list interfaces":
        return " ".join(interfaces)
    elif command == "list interfaces up":
        tooutput = []
        for i in interfaces:
            j = open(f"/sys/class/net/{i}/operstate")
            if j.read().strip() == "up":
                tooutput.append(i)
        return " ".join(tooutput)
    elif command.startswith("interface"):
        a = command.split(" ")
        if a[2] == "wake":
            if a[1].startswith("e") and a[1] in interfaces:
                print(f"{a[1]} setting state up")
                subprocess.run(["ip", "link", "set", a[1], "up"])
                print(f"{a[1]} get network ip by dhcp")
                subprocess.run(["dhcpcd", a[1]])
                return "ok"
            elif a[1].startswith("w") and a[1] in interfaces:
                print(f"{a[1]} setting state up")
                subprocess.run(["ip", "link", "set", a[1], "up"])
                print(f"{a[1]} disable rfkill")
                subprocess.run(["rfkill", "unblock", "wifi"])
                print(f"{a[1]} create config")
                try:
                    result = subprocess.run(["wpa_passphrase", a[3], a[4]],
                    capture_output=True,
                    text=True,
                    check=True)
                except:
                    result = subprocess.run(["wpa_passphrase", a[3]],
                    capture_output=True,
                    text=True,
                    check=True)
                file = open(f"/etc/{a[1]}_unet.conf", "w")
                file.write(result.stdout)
                file.close()
                subprocess.run(["wpa_supplicant", "-B", "-i", a[1], "-c", f"/etc/{a[1]}_unet.conf"])
                subprocess.run(["dhcpcd", "-w", a[1]])
                return "ok"
            elif a[2] in interfaces:
                return "available, not supported"
            else:
                return "not exist"
        elif a[1] == "scan" and a[2].startswith("w"):
            return "\n".join(scanwifi(a[2]))

def scanwifi(iface):
    result = subprocess.run(["iw", "dev", iface, "scan"],
                            capture_output=True,
                            text=True)
    
    ssids = []
    
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("SSID:"):
            ssid = line[len("SSID:"):].strip()
            if ssid:
                ssids.append(ssid)
    return ssids

print("creating interface list...")
interfaces = [i for i in os.listdir("/sys/class/net/") if i != "lo"]
print("found interfaces ", end="")
for i in interfaces:
    print(i + " ", end="")
print("")

FIFOin = "/tmp/uzbeknetwork.fifo.in"
FIFOout = "/tmp/uzbeknetwork.fifo.out"

print(f"FIFO input located at {FIFOin}")
if not os.path.exists(FIFOin):
    os.mkfifo(FIFOin)
print(f"FIFO input created at {FIFOin}")

print(f"FIFO output located at {FIFOout}")
if not os.path.exists(FIFOout):
    os.mkfifo(FIFOout)
print(f"FIFO output created at {FIFOout}")

print(f"running autorun commands...")
try:
    for i in open("/etc/uzbeknetwork.autostart").read().split("\n"):
        print(command(i))
    print("autorun command list end")
except:
    print("no autorun file, skipping...")

print("now polling fifo")
while True:
    with open(FIFOin, "r") as fifo_in, open(FIFOout, "w") as fifo_out:
        for line in fifo_in:
            interfaces = [i for i in os.listdir("/sys/class/net/") if i != "lo"]
            line = line.strip()
            if not line:
                continue

            print(f"received line: {line}")
            fifo_out.write(command(line) + "\n")
        fifo_out.flush()
