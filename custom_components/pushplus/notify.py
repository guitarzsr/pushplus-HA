"""PushPlus notification service."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_TITLE,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
from homeassistant.const import CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import (
    API_ENDPOINT,
    CHANNELS,
    CHANNELS_NEED_OPTION,
    CONF_CHANNEL,
    CONF_OPTION,
    CONF_TEMPLATE,
    CONF_TOPIC,
    DEFAULT_CHANNEL,
    DEFAULT_NAME,
    DEFAULT_TEMPLATE,
    ERROR_CODES,
    RATE_LIMIT_RESET_SECONDS,
    REQUEST_TIMEOUT,
    TEMPLATES,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_TOKEN): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_TEMPLATE, default=DEFAULT_TEMPLATE): vol.In(TEMPLATES),
        vol.Optional(CONF_CHANNEL, default=DEFAULT_CHANNEL): vol.In(CHANNELS),
        vol.Optional(CONF_OPTION, default=""): cv.string,
        vol.Optional(CONF_TOPIC, default=""): cv.string,
    }
)


def get_service(
    hass: HomeAssistant,
    config: dict[str, Any],
    discovery_info: dict[str, Any] | None = None,
) -> PushPlusNotificationService:
    """Get the PushPlus notification service."""
    return PushPlusNotificationService(
        hass,
        token=config[CONF_TOKEN],
        topic=config.get(CONF_TOPIC, ""),
        template=config.get(CONF_TEMPLATE, DEFAULT_TEMPLATE),
        channel=config.get(CONF_CHANNEL, DEFAULT_CHANNEL),
        option=config.get(CONF_OPTION, ""),
    )


class PushPlusNotificationService(BaseNotificationService):
    """Implement the notification service for PushPlus."""

    def __init__(
        self,
        hass: HomeAssistant,
        token: str,
        topic: str = "",
        template: str = DEFAULT_TEMPLATE,
        channel: str = DEFAULT_CHANNEL,
        option: str = "",
    ) -> None:
        """Initialize the service."""
        self.hass = hass
        self._token = token
        self._topic = topic
        self._template = template
        self._channel = channel
        self._option = option
        self._rate_limited_until: float | None = None

    def send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send a message to PushPlus (called in executor by HA)."""
        asyncio.run_coroutine_threadsafe(
            self.async_send_message(message, **kwargs),
            self.hass.loop,
        ).result()

    async def async_send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send a message to PushPlus asynchronously."""
        title = kwargs.get(ATTR_TITLE)

        if not title:
            _LOGGER.error("PushPlus: 标题不能为空")
            return

        if self._rate_limited_until is not None:
            now_ts = datetime.now().timestamp()
            if now_ts < self._rate_limited_until:
                remaining = int(self._rate_limited_until - now_ts)
                _LOGGER.warning(
                    "PushPlus: 处于限流状态，%d 秒后恢复", remaining
                )
                return
            self._rate_limited_until = None
            _LOGGER.info("PushPlus: 限流已解除，恢复正常推送")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"{now} {message}"

        payload: dict[str, Any] = {
            "token": self._token,
            "title": title,
            "content": content,
            "template": self._template,
            "channel": self._channel,
        }

        if self._topic:
            payload["topic"] = self._topic

        if self._option and self._channel in CHANNELS_NEED_OPTION:
            payload["option"] = self._option

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    API_ENDPOINT,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
        except asyncio.TimeoutError:
            _LOGGER.error("PushPlus: 请求超时（%d 秒）", REQUEST_TIMEOUT)
            return
        except aiohttp.ClientConnectorError:
            _LOGGER.error("PushPlus: 无法连接到 pushplus.plus，请检查网络")
            return
        except aiohttp.ClientError as err:
            _LOGGER.error("PushPlus: 请求异常：%s", err)
            return
        except ValueError:
            _LOGGER.error("PushPlus: 响应不是有效的 JSON")
            return

        code = data.get("code", -1)
        msg = data.get("msg", "")

        if code == 200:
            short_code = data.get("data", "")
            _LOGGER.debug("PushPlus 消息已提交，流水号: %s", short_code)
        elif code == 900:
            self._rate_limited_until = (
                datetime.now().timestamp() + RATE_LIMIT_RESET_SECONDS
            )
            _LOGGER.error(
                "PushPlus 返回限流 code=%d：%s，将暂停推送 %d 秒",
                code,
                ERROR_CODES.get(code, msg),
                RATE_LIMIT_RESET_SECONDS,
            )
        elif code == 903:
            _LOGGER.error(
                "PushPlus 返回错误 code=%d：%s（%s），请检查 Token 是否正确",
                code,
                ERROR_CODES.get(code, "未知错误"),
                msg,
            )
        else:
            _LOGGER.error(
                "PushPlus 返回错误 code=%d：%s（%s）",
                code,
                ERROR_CODES.get(code, "未知错误"),
                msg,
            )
