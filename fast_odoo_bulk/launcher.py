"""
Launch an in-process loader inside a containerized Odoo via ``docker exec ... odoo shell``.

This runs on the *host* (no Odoo import here), pipes an entrypoint script into the Odoo
container's ``odoo shell`` stdin, and forwards loader arguments through the ``LOADER_ARGS``
environment variable. The entrypoint (executed where ``env`` is in scope) builds an
:class:`fast_odoo_bulk.client.InProcessClient` and calls the project's migration ``run``.

Usage (programmatic)::

    from fast_odoo_bulk.launcher import run_inproc
    run_inproc(container="odoo19", db="rio_teapa_test",
               entry_script="/abs/path/_inproc_entry.py",
               loader_args="--section invoices --limit 50")

or via CLI::

    python -m fast_odoo_bulk.launcher --container odoo19 --db rio_teapa_test \\
        --entry import_code/_inproc_entry.py -- --section invoices --limit 50
"""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence


def build_command(
    container: str,
    db: str,
    *,
    loader_args: str = "",
    extra_env: Optional[dict[str, str]] = None,
    docker: str = "docker",
    odoo_bin: str = "odoo",
) -> list[str]:
    """Return the ``docker exec`` argv that runs ``odoo shell`` reading a script from stdin."""
    cmd = [docker, "exec", "-i", "-e", f"LOADER_ARGS={loader_args}"]
    for key, value in (extra_env or {}).items():
        cmd += ["-e", f"{key}={value}"]
    cmd += [container, odoo_bin, "shell", "-d", db, "--no-http"]
    return cmd


def run_inproc(
    container: str,
    db: str,
    entry_script: str,
    *,
    loader_args: str = "",
    extra_env: Optional[dict[str, str]] = None,
    docker: str = "docker",
    odoo_bin: str = "odoo",
) -> int:
    """Pipe ``entry_script`` into the container's ``odoo shell`` and return its exit code."""
    script = Path(entry_script).read_bytes()
    cmd = build_command(
        container, db, loader_args=loader_args, extra_env=extra_env,
        docker=docker, odoo_bin=odoo_bin,
    )
    print("[fast_odoo_bulk] " + " ".join(shlex.quote(c) for c in cmd), file=sys.stderr)
    proc = subprocess.run(cmd, input=script)
    return proc.returncode


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run an in-process Odoo loader via odoo shell")
    parser.add_argument("--container", required=True, help="Odoo container name/id")
    parser.add_argument("--db", required=True, help="Odoo database name")
    parser.add_argument("--entry", required=True, help="Path to the odoo-shell entrypoint .py")
    parser.add_argument("--docker", default="docker", help="docker binary (e.g. 'sudo docker')")
    parser.add_argument("--odoo-bin", default="odoo", help="odoo binary inside the container")
    parser.add_argument(
        "loader_args", nargs=argparse.REMAINDER,
        help="Args forwarded to the loader (prefix with --), e.g. -- --section invoices --limit 50",
    )
    args = parser.parse_args(argv)
    loader_args = args.loader_args
    if loader_args and loader_args[0] == "--":
        loader_args = loader_args[1:]
    return run_inproc(
        container=args.container,
        db=args.db,
        entry_script=args.entry,
        loader_args=" ".join(loader_args),
        docker=args.docker,
        odoo_bin=args.odoo_bin,
    )


if __name__ == "__main__":
    raise SystemExit(main())
