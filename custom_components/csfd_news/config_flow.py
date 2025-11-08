"""Config flow for CSFD News integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class CSFDNewsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CSFD News."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Check if already configured
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            # Create the config entry
            return self.async_create_entry(
                title="CSFD News",
                data={},
            )

        # Show the configuration form (empty in this case)
        return self.async_show_form(
            step_id="user",
        )

    async def async_step_import(self, import_config: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        # Check if already configured
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        # Create entry from YAML import
        return self.async_create_entry(
            title="CSFD News",
            data={},
        )
