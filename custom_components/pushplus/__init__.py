"""PushPlus notification integration for Home Assistant."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DEFAULT_NAME, DOMAIN
from .notify import PushPlusNotificationService

_LOGGER = logging.getLogger(__name__)

NOTIFY_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("message"): cv.string,
        vol.Optional("title"): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
    """Integration setup (YAML path handled by notify platform)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PushPlus from a config entry."""
    _LOGGER.debug("Setting up PushPlus config entry: %s", entry.entry_id)

    data = dict(entry.data)
    service_name = data.get(CONF_NAME, DEFAULT_NAME)

    service = PushPlusNotificationService(
        hass,
        token=data["token"],
        topic=data.get("topic", ""),
        template=data.get("template", "html"),
        channel=data.get("channel", "wechat"),
        option=data.get("option", ""),
    )

    async def _send_message(call: ServiceCall) -> None:
        """Handle service call to send notification."""
        await service.async_send_message(
            call.data.get("message", ""),
            title=call.data.get("title"),
        )

    hass.services.async_register(
        "notify",
        service_name,
        _send_message,
        schema=NOTIFY_SERVICE_SCHEMA,
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = data
    hass.data[DOMAIN][f"{entry.entry_id}_service_name"] = service_name

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    service_name = hass.data[DOMAIN].pop(f"{entry.entry_id}_service_name", None)
    if service_name:
        hass.services.async_remove("notify", service_name)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
