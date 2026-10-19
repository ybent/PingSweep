# recon

`recon` is a small IPv4 ping-sweep tool written in Python. It was created as
a fun side project for learning about network reconnaissance, subprocesses,
and running tasks in parallel.

This is a simple learning project, not a replacement for a production network
scanner. 

> Only use it on systems and networks that you own.

## What it does

- Accepts a single IPv4 address or an IPv4 CIDR network.
- Sends one ping to each target.
- Runs multiple pings concurrently.
- Shows a small spinner while the scan is running.
- Prints reachable hosts, the total number of reachable hosts, and elapsed time.
- Uses the platform's `ping` command on Windows, Linux, and macOS-style systems.

## Requirements

- Python 3.10 or newer
- The system `ping` command
- No third-party Python packages

## Usage

Scan a single host:

```powershell
python recon.py 192.168.1.10
```

Scan an IPv4 network:

```powershell
python recon.py 192.168.1.0/24
```

Change the maximum number of concurrent pings:

```powershell
python recon.py 192.168.1.0/24 --workers 100
```

Change the timeout for each ping:

```powershell
python recon.py 192.168.1.0/24 --timeout 1
```

Both options can be used together:

```powershell
python recon.py 192.168.1.0/24 --timeout 0.25 --workers 512
```

## Options

| Option | Default | Description |
| --- | ---: | --- |
| `target` | required | An IPv4 address or CIDR network |
| `--timeout` | `0.5` | Ping timeout in seconds |
| `--workers` | `256` | Number of parallel pings, from 1 to 1024 |

## Example output

```text
| Scanning hosts...
192.168.1.1 reachable
192.168.1.10 reachable

2/254 hosts reachable
Elapsed time: 0.62 seconds
```

## Customizing the spinner

The spinner settings are near the top of `recon.py`:

```python
spinnerText = "Scanning hosts..."
SPINNER_FRAMES = "|/-\\"
SPINNER_COLOR = "\033[33m"
TEXT_COLOR = ""
RESET_COLOR = "\033[0m"
```

You can change the message or animation frames to match your preference. This spinner is created by  [BenjaminUrquhart](https://github.com/BenjaminUrquhart/loading-spinner)


