# Copyright 2026 Johan Hallbäck
# See LICENSE file for licensing details.

"""Functions for managing and interacting with the workload.

The intention is that this module could be used outside the context of a charm.
"""

import logging
import subprocess

from charmlibs import apt
from charms.operator_libs_linux.v1.systemd import (
    service_enable,
    service_running,
    service_start,
    service_restart,
    service_failed
)
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


# Functions for managing the workload process on the local machine:


def install() -> None:
    """Install the workload (by installing a snap, for example)."""

    # This command checks for dependencies, installs GPG keys and runs apt update
    cmd = (
        "curl -1sLf https://dl.cloudsmith.io/public/isc/stork/cfg/setup/bash.deb.sh"
        "| sudo bash"
    )

    try:
        subprocess.run(cmd, shell=True, check=True)
        apt.add_package(["isc-stork-agent"])
        service_enable("isc-stork-agent")
    except Exception as e:
        # Throw an error to ensure automatic retry later
        logger.error(f"Error installing isc-stork-agent: {str(e)}")
        sys.exit(1)


def start() -> None:
    """Start the workload (by running a commamd, for example)."""
    if not service_running("isc-stork-agent"):
        service_start("isc-stork-agent")

    if service_failed("isc-stork-agent"):
        logger.error(f"Error starting isc-stork-agent")
        sys.exit(1)


def get_version() -> str | None:
    """Get the running version of the workload."""
    # If we can't get the version, it is assumed the software isn't installed
    try:
        cmd = ["stork-agent", "--version"]
        sp = subprocess.run(cmd, check=True, capture_output=True, encoding="utf-8")
        logger.info(f"stork_agent.get_version()): got version: {sp.stdout}")
        # Remove trailing newline
        return sp.stdout.rstrip()
    except Exception as e:
        logger.warning(f"stork_agent.get_version()): Failed to get version: {e}")
        return None


def render_and_reload(agent_host, server_url) -> int:
    # This should later only reload on actual config change
    env = Environment(loader=FileSystemLoader("templates"),
            keep_trailing_newline=True, trim_blocks=False)

    agent_env_tmpl = env.get_template("agent.env.j2")
    agent_env = agent_env_tmpl.render(
        agent_host=agent_host,
        server_url=server_url,
    )
    with open("/etc/stork/agent.env", "w") as file:
        file.write(agent_env)

    # reload/restart here
    service_restart("isc-stork-agent")