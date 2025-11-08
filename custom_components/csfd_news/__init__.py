"""The CSFD News integration."""
import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the CSFD News component from YAML (legacy support)."""
    hass.data.setdefault(DOMAIN, {})

    # Check if YAML configuration exists
    if DOMAIN in config:
        # Trigger import flow to migrate to config entry
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data={},
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CSFD News from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Register Lovelace card as frontend resource
    _register_lovelace_card(hass)

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


def _register_lovelace_card(hass: HomeAssistant) -> None:
    """Register the Lovelace card as a frontend resource."""
    # Get the path to the integration directory
    integration_dir = os.path.dirname(__file__)

    # Register static path for serving the card JavaScript file
    hass.http.register_static_path(
        "/csfd_news",
        integration_dir,
        cache_headers=False
    )

    _LOGGER.info(
        "CSFD News Lovelace card available at /csfd_news/csfd-news-card.js - "
        "Add it to Lovelace resources to use the card"
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
