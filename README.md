# PushPlus for Home Assistant

[![GitHub Release][badge_github_release_version]][github_release_link]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

[PushPlus](http://www.pushplus.plus)（推送加）通知服务的 Home Assistant 集成。

支持微信公众号、企业微信、钉钉、飞书、Bark、邮件、短信、语音、APP 等 **9 种推送渠道**。

## ✨ 特性

- 🇨🇳 **完整中文界面** — 配置 UI 全中文
- 🎛️ **配置 UI** — 通过 HA 界面添加，无需编辑 YAML
- 📡 **多渠道路由** — 微信、企业微信、Webhook、邮件、短信、语音等 9 种渠道
- 📝 **多模板** — html / txt / json / markdown 四种消息格式
- 👥 **群组推送** — 支持 PushPlus 群组编码（topic）
- 🔐 **安全** — Token 以密码字段输入
- ⚡ **智能错误处理** — 限流自动退避、Token 失效提示、错误码中文翻译
- 🔄 **向后兼容** — 同时支持 YAML 配置方式

## 📦 安装

### 方式一：HACS（推荐）

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=guitarzsr&repository=pushplus-HA&category=Integration)

1. HACS → 自定义仓库 → 添加 `https://github.com/guitarzsr/pushplus-HA`
2. 搜索 "PushPlus" 并安装
3. 重启 Home Assistant

### 方式二：手动安装

```bash
# 将 custom_components/pushplus/ 复制到 HA 配置目录
cp -r custom_components/pushplus /config/custom_components/pushplus/
```

## ⚙️ 配置

### 通过 UI 配置（推荐）

1. **获取 Token**：登录 [pushplus.plus](http://www.pushplus.plus) → 个人中心 → 获取 Token
2. **HA 中添加**：设置 → 设备与服务 → 添加集成 → 搜索 "PushPlus"
3. **填写配置**：

| 字段 | 必填 | 说明 |
|---|---|---|
| 名称 | ✅ | 自定义服务名称（默认 PushPlus） |
| Token | ✅ | 你的 PushPlus token |
| 消息模板 | ✅ | html / txt / json / markdown |
| 发送渠道 | ✅ | 9 种渠道可选（默认微信公众号） |
| 群组编码 | ❌ | 推送到群组时填写 |
| 渠道配置编码 | ❌ | Webhook/企微应用/邮箱渠道所需 |

### 多渠道路由

你可以添加**多个 PushPlus 集成**，每个配置不同的渠道，实现消息分流：

```
notify.pushplus → 微信（默认）
notify.pushplus_email → 邮件
notify.pushplus_webhook → 企业微信机器人
```

### YAML 配置（兼容旧版）

```yaml
notify:
  - platform: pushplus
    name: pushplus
    token: !secret pushplus_token
    template: html
    channel: wechat
    topic: 群组编码  # 可选
    option: 渠道配置  # 可选（webhook/cp/mail 渠道）
```

## 🚀 使用

集成提供三种推送方式，按需选择：

### 方式一：直接调用服务（精确控制）

适合自动化/脚本中写死推送内容，如门铃、漏水告警等固定场景。

```yaml
action: notify.pushplus
data:
  title: "门铃响了"
  message: "前门有人按门铃"
```

**测试**：开发者工具 → 动作 → `notify.pushplus` → 填 title + message → 调用。

### 方式二：蓝图（GUI 可视化）

适合在 HA 界面中灵活配置触发条件和推送模板，无需写 YAML。

1. [下载蓝图文件](https://github.com/guitarzsr/pushplus-HA/raw/master/blueprints/automation/pushplus/pushplus_event_push.yaml)
2. HA → 设置 → 自动化与场景 → ⋮ → 导入蓝图 → 粘贴 → 把下载的 YAML 内容贴进去
3. 蓝图列表中选择「PushPlus 通用推送」→ 创建自动化
4. 选择触发条件（如定时、设备状态变更、事件等）
5. 填写推送标题和内容（支持 Jinja 模板）
6. 保存后手动「立即运行」测试

### 方式三：系统通知接管（零配置，≈ Unraid 效果）

所有 HA 系统通知（集成离线、组件报错等）自动推送到微信。

复制以下自动化到 HA：

```yaml
alias: "📢 系统通知 → PushPlus"
mode: single
triggers:
  - trigger: event
    event_type: call_service
    event_data:
      domain: persistent_notification
      service: create
actions:
  - action: notify.pushplus
    data:
      title: "{{ trigger.event.data.service_data.title | default('HA 系统通知') }}"
      message: "{{ trigger.event.data.service_data.message | default('') }}"
```

**测试**：开发者工具 → 动作 → `persistent_notification.create` → 填 title + message → 调用。

### 方式对比

| 方式 | 配置难度 | 灵活度 | 适用场景 |
|---|---|---|---|
| 直接调用 | 低 | 中 | 固定通知（门铃、漏水） |
| 蓝图 | 中 | 高 | GUI 可视化配置，支持模板 |
| 系统接管 | 低 | 低 | HA 报错自动推送，零维护 |

## 📖 发送渠道说明

| 渠道 | 类型 | 说明 |
|---|---|---|
| 微信公众号 | 免费 | 默认渠道，通过微信公众号推送 |
| 第三方 Webhook | 免费 | 企业微信/钉钉/飞书/Bark/Gotify 等 |
| 企业微信应用 | 免费 | 企业微信自建应用推送 |
| 邮件 | 免费 | 邮箱推送 |
| 短信 | 付费 | 10 积分/条（0.1 元） |
| 语音电话 | 付费 | 30 积分/次（0.3 元） |
| PushPlus App | 免费 | Android / 鸿蒙 / iOS |
| 浏览器/桌面插件 | 免费 | Chrome 扩展或桌面应用 |
| 微信 ClawBot | 免费 | 通过微信 ClawBot 推送 |

> Webhook、企业微信应用、邮件渠道需先在 PushPlus 个人中心配置对应渠道编码，填入「渠道配置编码」字段。

## 🔧 错误处理

集成自动处理 PushPlus 返回的错误码并显示中文提示：

| 错误码 | 处理方式 |
|---|---|
| 200 | ✅ 消息已提交 |
| 900 | ⚠️ 自动限流退避，后续推送跳过 |
| 903 | ❌ Token 无效，提示检查 |
| 888 | ❌ 积分不足（短信/语音渠道） |
| 905 | ❌ 未实名认证 |
| 500 | ⚠️ 服务异常，提示等后重试 |

## 📝 更新日志

### v2.0.3
- Rewrite `__init__.py`: direct notify service registration (bypass EntityComponent)
- Add `integration_type: service` to manifest
- Remove all dead imports

### v2.0.2
- Remove token validation API call on config save
- Upgrade endpoint to HTTPS
- Rate-limit auto-reset after 300s
- Replace requests with aiohttp
- Add `translations/en.json`

### v2.0.1
- Add channel & option support
- Add smart error handling (14 error codes)
- Add HD icon (1024px source)

### v2.0.0
- Config Flow UI (no more YAML editing)
- 9 send channel routing
- Complete zh-Hans + en translations
- Smart error handling with rate-limit backoff
- Blueprint for system notification forwarding
- POST + JSON body (replaces GET + query string)
- Min HA version: 2024.1.0

### v1.3
- 初始版本（仅 YAML 配置）

## 🤝 贡献

欢迎提 Issue 和 PR。

Fork 自 [wubin2/pushplus](https://github.com/wubin2/pushplus)（v1.3 原版），v2.0 起独立维护。

本仓库代码由 **DeepSeek V4 Pro** 生成，**GLM 5.1** 进行代码审查。

[badge_github_release_version]: https://img.shields.io/github/v/release/guitarzsr/pushplus-HA?style=for-the-badge&label=release
[github_release_link]: https://github.com/guitarzsr/pushplus-HA/releases
