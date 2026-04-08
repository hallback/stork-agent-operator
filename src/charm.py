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
        framework.observe(self.on.config_changed, self._on_config_changed)
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

    def _on_config_changed(self, event: ops.ConfigChangedEvent):
        logger.info(f"stork configuration changed: {event}")
        relation_data = self._stork_relation_data
        if relation_data is None:
            return
        agent_host, server_url = relation_data

        stork_agent.render_and_reload(agent_host, server_url)

    def _on_stork_relation_changed(self, event: ops.RelationJoinedEvent):
        logger.info(f"stork relation changed: {event}")
        relation_data = self._stork_relation_data
        if relation_data is None:
            return
        agent_host, server_url = relation_data

        stork_agent.render_and_reload(agent_host, server_url)

    @property
    def _stork_relation_data(self) -> tuple[str, str] | None:
        # My IP for the stork relation
        agent_host = str(self.model.get_binding("stork").network.bind_address)

        # Get the remote ip on the stork relation
        relation = self.model.get_relation("stork")
        server_ip = ""
        if relation is not None:
            for unit in relation.units:
                unit_data = relation.data[unit]
                server_ip = unit_data.get("ingress-address") or unit_data.get("private-address") or ""
                if server_ip:
                    logger.info(f"_stork-relation-data(): Found server_ip {server_ip} on unit {unit}")
                    break
        if not server_ip:
            logger.info(f"_stork-relation-data(): No server_ip found on the stork relation yet, skipping rendering")
            return None

        # TODO: We need to fix later so that this respects protocol and port
        server_url = f"http://{server_ip}:8080"

        return agent_host, server_url


if __name__ == "__main__":  # pragma: nocover
    ops.main(StorkAgentOperatorCharm)
