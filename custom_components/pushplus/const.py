"""Constants for PushPlus integration."""
from typing import Final

DOMAIN: Final = "pushplus"

CONF_TOKEN: Final = "token"
CONF_TOPIC: Final = "topic"
CONF_TEMPLATE: Final = "template"
CONF_CHANNEL: Final = "channel"
CONF_OPTION: Final = "option"

DEFAULT_TEMPLATE: Final = "html"
DEFAULT_NAME: Final = "PushPlus"
DEFAULT_CHANNEL: Final = "wechat"

API_ENDPOINT: Final = "http://www.pushplus.plus/send"
API_BATCH_ENDPOINT: Final = "http://www.pushplus.plus/batchSend"

DOC_URL: Final = "https://www.pushplus.plus/doc/guide/api.html"
DOC_CHANNEL_URL: Final = "https://www.pushplus.plus/doc/channel/"

TEMPLATES: Final = ["html", "txt", "json", "markdown"]

TEMPLATE_LABELS: Final = {
    "html": "HTML（html）",
    "txt": "纯文本（txt）",
    "json": "JSON（json）",
    "markdown": "Markdown（markdown）",
}

CHANNELS: Final = [
    "wechat",
    "webhook",
    "cp",
    "mail",
    "sms",
    "voice",
    "app",
    "extension",
    "clawbot",
]

CHANNELS_NEED_OPTION: Final = ["webhook", "cp", "mail"]

CHANNEL_LABELS: Final = {
    "wechat": "微信公众号（wechat）",
    "webhook": "第三方 Webhook（webhook）",
    "cp": "企业微信应用（cp）",
    "mail": "邮件（mail）",
    "sms": "短信（sms，付费）",
    "voice": "语音电话（voice，付费）",
    "app": "PushPlus APP（app）",
    "extension": "浏览器/桌面插件（extension）",
    "clawbot": "微信 ClawBot（clawbot）",
}

ERROR_CODES: Final = {
    200: "请求成功",
    302: "未登录，请检查 Token",
    401: "请求未授权",
    403: "IP 未授权",
    500: "PushPlus 服务异常，请稍后重试",
    600: "数据异常，操作失败",
    805: "无权查看",
    888: "积分不足，需要充值",
    900: "请求频率过高，请减少推送频率",
    903: "无效的 Token",
    905: "账户未实名认证",
    999: "服务端验证错误",
}
