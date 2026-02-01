# UzbekNetwork docs

## Where to talk with UzbekNetwork?

UzbekNetwork uses two FIFO files, which you can use to talk with UzbekNetwork. If you want simple connect, try this command:

```shell
echo "your command here" | sudo tee /tmp/uzbeknetwork.fifo.in && cat /tmp/uzbeknetwork.fifo.out
```

## Listing interfaces

To list all interfaces, you can use command:

```uzbekshell
list interfaces
```

This will send you interface list, splitted by space. UzbekNetwork can understand interfaces, starting with e (wired connections) and with w (wireless connections)

## Connecting

### Ethernet

```uzbekshell
interface wake YOUR_INTERFACE 
```

This will "wake" your interface

### Wi-Fi

```uzbekshell
interface wake YOUR_INTERFACE SSID PASS
```

This will "wake" your interface using given ssid and pass

## Scanning Wi-Fi

```uzbekshell
interface scan YOUR_INTERFACE
```

This will scan and send you a list of networks splitted by newline

## How to connect automatically?

When started, UzbekNetwork automatically reads file `/etc/uzbeknetwork.autostart`. Just throw bunch of commands in this file.
