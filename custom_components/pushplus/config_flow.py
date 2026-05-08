"""Config flow for PushPlus integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_TOKEN
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CHANNEL_LABELS,
    CHANNELS,
    CHANNELS_NEED_OPTION,
    CONF_CHANNEL,
    CONF_OPTION,
    CONF_TEMPLATE,
    CONF_TOPIC,
    DEFAULT_CHANNEL,
    DEFAULT_NAME,
    DEFAULT_TEMPLATE,
    DOC_URL,
    DOMAIN,
    TEMPLATE_LABELS,
    TEMPLATES,
)

_LOGGER = logging.getLogger(__name__)

DESCRIPTION_TEMPLATE = (
    "输入 PushPlus 推送配置。\n\n"
    "Token 获取：登录 pushplus.plus → 个人中心 → 获取 Token\n\n"
    "[📖 PushPlus 消息接口文档]({doc_url})"
).format(doc_url=DOC_URL)


def _build_schema(user_input: dict[str, Any] | None = None) -> vol.Schema:
    """Build the config flow schema based on current input."""
    schema = {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Optional(CONF_TEMPLATE, default=DEFAULT_TEMPLATE): vol.In(
            {k: v for k, v in TEMPLATE_LABELS.items()}
        ),
        vol.Optional(CONF_CHANNEL, default=DEFAULT_CHANNEL): vol.In(
            {k: v for k, v in CHANNEL_LABELS.items()}
        ),
        vol.Optional(CONF_TOPIC, default=""): cv.string,
    }

    channel = DEFAULT_CHANNEL
    if user_input and CONF_CHANNEL in user_input:
        channel = user_input[CONF_CHANNEL]

    if channel in CHANNELS_NEED_OPTION:
        schema[vol.Optional(CONF_OPTION, default="")] = cv.string

    return vol.Schema(schema)


class PushPlusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PushPlus."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if CONF_OPTION not in user_input:
                channel = user_input.get(CONF_CHANNEL, DEFAULT_CHANNEL)
                if channel in CHANNELS_NEED_OPTION:
                    user_input[CONF_OPTION] = ""
                else:
                    user_input[CONF_OPTION] = ""

            token = user_input[CONF_TOKEN]
            name = user_input.get(CONF_NAME, DEFAULT_NAME)
            unique_id = f"{token[:8]}_{user_input.get(CONF_CHANNEL, DEFAULT_CHANNEL)}"

            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=name,
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input),
            description_placeholders={"doc_url": DOC_URL},
            errors=errors,
        )
