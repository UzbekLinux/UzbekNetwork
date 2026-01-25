#!/usr/bin/python3
import os
import subprocess

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

while True:
    with open(FIFOin, "r") as fifo_in, open(FIFOout, "w") as fifo_out:
        for line in fifo_in:
            interfaces = [i for i in os.listdir("/sys/class/net/") if i != "lo"]
            line = line.strip()
            if not line:
                continue

            print(f"received line: {line}")
            if line == "ping":
                fifo_out.write("pong\n")
            elif line == "list interfaces":
                fifo_out.write(" ".join(interfaces) + "\n")
            elif line == "list interfaces up":
                tooutput = []
                for i in interfaces:
                    j = open(f"/sys/class/net/{i}/operstate")
                    if j.read().strip() == "up":
                        tooutput.append(i)
                    fifo_out.write(" ".join(tooutput) + "\n")
            elif line.startswith("interface"):
                a = line.split(" ")
                if a[1] == "wake":
                    if a[2].startswith("e") and a[2] in interfaces:
                        print(f"{a[1]} setting state up")
                        subprocess.run(["ip", "link", "set", a[2], "up"])
                        print(f"{a[1]} get network ip by dhcp")
                        subprocess.run(["dhcpcd", a[2]])
                        fifo_out.write("ok")
                    elif a[2].startswith("w") and a[2] in interfaces:
                        print(f"{a[1]} setting state up")
                        subprocess.run(["ip", "link", "set", a[2], "up"])
                        print(f"{a[1]} disable rfkill")
                        subprocess.run(["rfkill", "unblock", "wifi"])
                        print(f"{a[1]} create config")
                        result = subprocess.run(["wpa_passphrase", a[3], a[4]],
                        capture_output=True,
                        text=True,
                        check=True)
                        file = open(f"/etc/{a[1]}_unet.conf", "w")
                        file.write(result.stdout)
                        file.close()
                        subprocess.run(["wpa_supplicant", "-B", "-i", a[2], "-c", f"/etc/{a[1]}_unet.conf"])
                        subprocess.run(["dhcpcd", "-w", a[2]])
                        fifo_out.write("ok")
                    elif a[2] in interfaces:
                        fifo_out.write("available, not supported")
                    else:
                        fifo_out.write("not exist")
                elif a[1] == "scan" and a[2].startswith("w"):
                    fifo_out.write("\n".join(scanwifi(a[2])) + "\n")
            fifo_out.flush()
