from __future__ import annotations

import argparse
import os
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path.home()
LOG_DIR = Path("/tmp/erp-local-backends/logs")
PID_DIR = Path("/tmp/erp-local-backends/pids")


@dataclass(frozen=True)
class BackendService:
    name: str
    repo: str
    port: int
    health_url: str
    env: dict[str, str]


SERVICES: tuple[BackendService, ...] = (
    BackendService(
        name="erp-api",
        repo="erp-api",
        port=7990,
        health_url="http://127.0.0.1:7990/healthz",
        env={
            "ERP_DATABASE_URL": "postgresql+psycopg://erp:erp@127.0.0.1:5433/erp",
        },
    ),
    BackendService(
        name="wms-api",
        repo="wms-api",
        port=8000,
        health_url="http://127.0.0.1:8000/healthz",
        env={
            "WMS_ENV": "dev",
            "WMS_TEST_DATABASE_URL": "",
            "WMS_DATABASE_URL": "postgresql+psycopg://wms:wms@127.0.0.1:5433/wms",
            "PMS_API_BASE_URL": "http://127.0.0.1:8005",
            "OMS_API_BASE_URL": "http://127.0.0.1:8010",
            "PROCUREMENT_API_BASE_URL": "http://127.0.0.1:8015",
            "LOGISTICS_API_BASE_URL": "http://127.0.0.1:8020",
        },
    ),
    BackendService(
        name="pms-api",
        repo="pms-api",
        port=8005,
        health_url="http://127.0.0.1:8005/healthz",
        env={
            "PMS_DATABASE_URL": "postgresql+psycopg://pms:pms@127.0.0.1:5433/pms",
        },
    ),
    BackendService(
        name="oms-api",
        repo="oms-api",
        port=8010,
        health_url="http://127.0.0.1:8010/healthz",
        env={
            "OMS_TEST_DATABASE_URL": "",
            "OMS_DATABASE_URL": "postgresql+psycopg://oms:oms@127.0.0.1:5433/oms",
            "PMS_API_BASE_URL": "http://127.0.0.1:8005",
        },
    ),
    BackendService(
        name="procurement-api",
        repo="procurement-api",
        port=8015,
        health_url="http://127.0.0.1:8015/healthz",
        env={
            "PROCUREMENT_ENV": "dev",
            "PROCUREMENT_DATABASE_URL": "postgresql+psycopg://procurement:procurement@127.0.0.1:5433/procurement",
            "WMS_API_BASE_URL": "http://127.0.0.1:8000",
            "PMS_API_BASE_URL": "http://127.0.0.1:8005",
            "PROCUREMENT_CORS_ORIGINS": "http://127.0.0.1:5176,http://localhost:5176",
        },
    ),
    BackendService(
        name="logistics-api",
        repo="logistics-api",
        port=8020,
        health_url="http://127.0.0.1:8020/healthz",
        env={
            "LOGISTICS_ENV": "dev",
            "LOGISTICS_TEST_DATABASE_URL": "",
            "LOGISTICS_DATABASE_URL": "postgresql+psycopg://logistics:logistics@127.0.0.1:5433/logistics",
            "WMS_API_BASE_URL": "http://127.0.0.1:8000",
        },
    ),
)


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def is_health_ok(url: str, *, timeout_seconds: float = 1.0) -> bool:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return 200 <= int(response.status) < 300
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def wait_for_health(service: BackendService, *, timeout_seconds: int) -> bool:
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        if is_health_ok(service.health_url):
            return True
        time.sleep(1)

    return False


def wait_until_stopped(pid: int, *, timeout_seconds: int) -> bool:
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        if not is_pid_running(pid):
            return True
        time.sleep(0.5)

    return not is_pid_running(pid)


def pid_file_for(service: BackendService) -> Path:
    return PID_DIR / f"{service.name}.pid"


def log_file_for(service: BackendService) -> Path:
    return LOG_DIR / f"{service.name}.log"


def read_pid(service: BackendService) -> int | None:
    path = pid_file_for(service)
    if not path.exists():
        return None

    try:
        return int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def remove_pid_file(service: BackendService) -> None:
    path = pid_file_for(service)
    if path.exists():
        path.unlink()


def is_pid_running(pid: int | None) -> bool:
    if pid is None or pid <= 0:
        return False

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True

    return True


def start_service(service: BackendService, *, wait_seconds: int, dry_run: bool) -> None:
    repo_dir = ROOT / service.repo
    if not repo_dir.exists():
        print(f"[missing] {service.name}: repo not found: {repo_dir}")
        return

    if is_health_ok(service.health_url):
        print(f"[ok] {service.name}: health ok at {service.health_url}")
        return

    if is_port_open(service.port):
        print(f"[warn] {service.name}: port {service.port} is open but health is not ok")
        return

    existing_pid = read_pid(service)
    if is_pid_running(existing_pid):
        print(f"[wait] {service.name}: pid {existing_pid} exists, waiting for health")
        if wait_for_health(service, timeout_seconds=wait_seconds):
            print(f"[ok] {service.name}: health ok at {service.health_url}")
        else:
            print(f"[fail] {service.name}: pid exists but health check failed")
        return

    command = ["make", "uvicorn"]
    print(f"[start] {service.name}: cd {repo_dir} && {' '.join(command)}")

    if dry_run:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    PID_DIR.mkdir(parents=True, exist_ok=True)

    log_path = log_file_for(service)
    log_file = log_path.open("ab")

    env = os.environ.copy()
    env.update(service.env)
    env["PYTHONPATH"] = "."

    process = subprocess.Popen(
        command,
        cwd=repo_dir,
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    pid_file_for(service).write_text(f"{process.pid}\n", encoding="utf-8")
    print(f"[pid] {service.name}: {process.pid}")
    print(f"[log] {service.name}: {log_path}")

    if wait_for_health(service, timeout_seconds=wait_seconds):
        print(f"[ok] {service.name}: health ok at {service.health_url}")
    else:
        print(f"[fail] {service.name}: health check failed after {wait_seconds}s")
        print(f"       log: {log_path}")


def stop_service(service: BackendService, *, wait_seconds: int, dry_run: bool) -> None:
    pid = read_pid(service)
    if not is_pid_running(pid):
        remove_pid_file(service)
        if is_port_open(service.port):
            print(
                f"[warn] {service.name}: no managed pid, but port {service.port} is open; "
                "skip killing unmanaged process"
            )
        else:
            print(f"[ok] {service.name}: already stopped")
        return

    assert pid is not None
    if dry_run:
        print(f"[dry-run] {service.name}: would terminate process group pid={pid}")
        return

    print(f"[stop] {service.name}: terminate process group pid={pid}")

    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        remove_pid_file(service)
        print(f"[ok] {service.name}: already stopped")
        return

    if wait_until_stopped(pid, timeout_seconds=wait_seconds):
        remove_pid_file(service)
        print(f"[ok] {service.name}: stopped")
        return

    print(f"[kill] {service.name}: force kill process group pid={pid}")
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass

    if wait_until_stopped(pid, timeout_seconds=5):
        remove_pid_file(service)
        print(f"[ok] {service.name}: stopped")
    else:
        print(f"[fail] {service.name}: failed to stop pid={pid}")


def restart_service(service: BackendService, *, wait_seconds: int, dry_run: bool) -> None:
    stop_service(service, wait_seconds=wait_seconds, dry_run=dry_run)
    start_service(service, wait_seconds=wait_seconds, dry_run=dry_run)


def show_status(service: BackendService) -> None:
    pid = read_pid(service)
    pid_status = f"pid={pid}" if is_pid_running(pid) else "pid=-"
    port_status = "open" if is_port_open(service.port) else "closed"
    health_status = "ok" if is_health_ok(service.health_url) else "fail"
    print(
        f"{service.name:16} port={service.port:<5} {pid_status:<12} "
        f"port_status={port_status:<6} health={health_status:<4} {service.health_url}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage local ERP backend stack.")
    parser.add_argument(
        "action",
        choices=("up", "down", "restart", "status"),
        nargs="?",
        default="up",
        help="Action to run. Defaults to up.",
    )
    parser.add_argument(
        "--service",
        action="append",
        choices=[service.name for service in SERVICES],
        help="Operate only selected service. Can be used multiple times.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without starting or stopping services.",
    )
    parser.add_argument(
        "--wait-seconds",
        type=int,
        default=30,
        help="Seconds to wait for health checks or process shutdown.",
    )
    return parser.parse_args()


def select_services(args: argparse.Namespace) -> list[BackendService]:
    selected_names = set(args.service or [])
    return [service for service in SERVICES if not selected_names or service.name in selected_names]


def main() -> None:
    args = parse_args()
    selected_services = select_services(args)

    if args.action == "status":
        for service in selected_services:
            show_status(service)
        return

    if args.action == "down":
        for service in reversed(selected_services):
            stop_service(service, wait_seconds=int(args.wait_seconds), dry_run=bool(args.dry_run))
        return

    if args.action == "restart":
        for service in selected_services:
            restart_service(
                service,
                wait_seconds=int(args.wait_seconds),
                dry_run=bool(args.dry_run),
            )
        return

    for service in selected_services:
        start_service(service, wait_seconds=int(args.wait_seconds), dry_run=bool(args.dry_run))


if __name__ == "__main__":
    main()
