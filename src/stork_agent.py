# Copyright 2026 Johan Hallbäck
# See LICENSE file for licensing details.

"""Functions for managing and interacting with the workload.

The intention is that this module could be used outside the context of a charm.
"""

import logging
import subprocess

from charmlibs import apt
logger = logging.getLogger(__name__)


# Functions for managing the workload process on the local machine:


def install() -> None:
    """Install the workload (by installing a snap, for example)."""
    # You'll need to implement this function.
    cmd = (
        "curl -1sLf https://dl.cloudsmith.io/public/isc/stork/cfg/setup/bash.deb.sh"
        "| sudo bash"
    )
    try:
        subprocess.run(cmd, shell=True, check=True)
        apt.add_package(["isc-stork-agent"])
    except Exception as e:
        # Throw an error to ensure automatic retry later
        logger.error(f"Error installing stork-agent: {str(e)}")
        sys.exit(1)

def start() -> None:
    """Start the workload (by running a commamd, for example)."""
    # You'll need to implement this function.
    # Ideally, this function should only return once the workload is ready to use.


# Functions for interacting with the workload, for example over HTTP:


def get_version() -> str | None:
    """Get the running version of the workload."""
    # You'll need to implement this function (or remove it if not needed).
    return None
