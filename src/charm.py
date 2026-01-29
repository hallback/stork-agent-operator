#!/usr/bin/env python3
# Copyright 2026 Johan Hallbäck
# See LICENSE file for licensing details.

"""Charm the application."""

import logging

import ops

# A standalone module for workload-specific logic (no charming concerns):
import stork_agent

logger = logging.getLogger(__name__)


class StorkAgentOperatorCharm(ops.CharmBase):
    """Charm the application."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on.install, self._on_install)
        framework.observe(self.on.start, self._on_start)
        framework.observe(self.on["stork"].relation_changed, self._on_stork_relation_changed)

    def _on_install(self, event: ops.InstallEvent):
        """Install the workload on the machine."""
        stork_agent.install()

    def _on_start(self, event: ops.StartEvent):
        """Handle start event."""
        self.unit.status = ops.MaintenanceStatus("starting workload")
        stork_agent.start()
        version = stork_agent.get_version()
        if version is not None:
            self.unit.set_workload_version(version)
        self.unit.status = ops.ActiveStatus()

    def _on_stork_relation_changed(self, event: ops.RelationJoinedEvent):
        logger.info(f"stork relation changed: {event}")


if __name__ == "__main__":  # pragma: nocover
    ops.main(StorkAgentOperatorCharm)
