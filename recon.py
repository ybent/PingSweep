"""
Author:     Younes Bentaiba Alili   
Description: Recon tool that performs a fast parallel IPv4 ping sweep. 
Github: github.com/ybent 

"""

import argparse
import concurrent.futures
import ipaddress
import platform
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Sequence

#############################################################################################
# Constants 
default_Timeout = 0.5
default_workers = 256
max_workers = 1024


spinnerText = "Scanning hosts..."
SPINNER_FRAMES = "|/-\\"
SPINNER_COLOR = "\033[33m"
TEXT_COLOR = ""
RESET_COLOR = "\033[0m"
#############################################################################################

@dataclass(frozen=True)
class HostResult:
    host: str
    reachable: bool

# Added spinner for visual feedback
# Creator of the spinner: https://github.com/BenjaminUrquhart/loading-spinner
def spinner(stop_event: threading.Event) -> None:
    frame = 1
    while not stop_event.is_set():
        print(
            "\r\033[2K"
            + SPINNER_COLOR
            + SPINNER_FRAMES[(frame - 1) % len(SPINNER_FRAMES)]
            + " "
            + RESET_COLOR
            + TEXT_COLOR
            + spinnerText
            + RESET_COLOR,
            end="",
            flush=True,
        )
        frame += 1
        time.sleep(0.1)
        if (frame - 1) % len(SPINNER_FRAMES) == 0:
            frame = 1


def expand_targets(target: str) -> list[str]:
    """Expand an IPv4 address or CIDR network into scan targets."""
    try:
        network = ipaddress.ip_network(target, strict=False)
    except ValueError as exc:
        raise ValueError(f"invalid IPv4 target: {target}") from exc
    if network.version != 4:
        raise ValueError("only IPv4 targets are supported")
    return [str(host) for host in network.hosts()] or [str(network.network_address)]


def _ping_command(host: str, timeout: float) -> list[str]:
    if platform.system().lower() == "windows":
        timeout_ms = max(1, int(timeout * 1000))
        return ["ping", "-4", "-n", "1", "-w", str(timeout_ms), host]
    return ["ping", "-4", "-c", "1", "-W", str(max(0.001, timeout)), host]


def ping_host(host: str, timeout: float) -> HostResult:
    try:
        completed = subprocess.run(
            _ping_command(host, timeout),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 1,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return HostResult(host, False)
    return HostResult(host, completed.returncode == 0)


def run_ping_sweep(
    targets: Sequence[str], timeout: float, workers: int
) -> int:
    reachable_hosts: list[str] = []
    started_at = time.perf_counter()

    stop_event = threading.Event()
    spinner_thread = threading.Thread(
        target=spinner,
        args=(stop_event,),
        daemon=True,
    )
    spinner_thread.start()
    try:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=workers
        ) as executor:
            futures = [
                executor.submit(ping_host, host, timeout)
                for host in targets
            ]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result.reachable:
                    reachable_hosts.append(result.host)
    finally:
        stop_event.set()
        spinner_thread.join()
        print("\r\033[2K", end="", flush=True)

    for host in sorted(reachable_hosts, key=ipaddress.ip_address):
        print(f"{host} reachable")

    reachable = len(reachable_hosts)
    total = len(targets)
    elapsed = time.perf_counter() - started_at
    print(f"\n{reachable}/{total} hosts reachable")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fast parallel IPv4 ping sweep."
    )
    parser.add_argument(
        "target",
        help="IPv4 address or CIDR network, for example 192.168.1.0/24",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=default_Timeout,
        help=f"ping timeout in seconds (default: {default_Timeout})",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=default_workers,
        help=f"parallel pings, 1-{max_workers} (default: {default_workers})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        targets = expand_targets(args.target)
        if args.timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        if not 0 < args.workers <= max_workers:
            raise ValueError(f"workers must be between 1 and {max_workers}")
    except ValueError as exc:
        parser.error(str(exc))

    return run_ping_sweep(targets, args.timeout, args.workers)


if __name__ == "__main__":
    sys.exit(main())
