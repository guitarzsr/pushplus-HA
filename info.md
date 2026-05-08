{% if prerelease %}
### ⚠️ 这是 Beta 版本！
{% endif %}

{% if version_installed and version_installed.split('.')[0] | int < 2 %}
### 🔄 从 v1.x 升级

v2.0 新增了配置 UI。升级后：

1. 在 HA UI 中重新添加 PushPlus 集成（设置 → 设备与服务 → 添加集成 → PushPlus）
2. 配置完成后，可移除 `configuration.yaml` 中的旧 YAML 配置
3. 重启 Home Assistant
{% endif %}
