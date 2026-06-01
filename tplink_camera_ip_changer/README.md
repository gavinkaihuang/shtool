# update_camera_ip.sh

自动查找局域网内指定摄像头的当前 IP 地址，更新 Frigate 配置文件并重启容器服务。

## 适用场景

摄像头（TP-Link 等）通过 DHCP 获取 IP，重启后 IP 可能发生变化，导致 Frigate 无法连接。  
本脚本通过 MAC 地址定位设备的最新 IP，自动完成配置更新和服务重启，无需手动介入。

## 运行环境

- Linux（Debian / Ubuntu）
- 已安装 `docker compose`（v2 插件形式）
- 执行用户具备 `sudo` 权限
- 脚本与目标摄像头处于同一局域网

## 脚本流程

1. **获取 IP**：发送广播 ping 刷新 ARP 表，依次通过 `ip neigh` 和 `arp -n` 查找 MAC 地址 `f8:ce:21:63:5e:b8` 对应的 IPv4 地址；未找到则报错退出。
2. **备份配置**：将 `/home/gavin/dockercompose/frigate/config.yml` 备份为 `config_MMDD.yml`（如 `config_0601.yml`）。
3. **修改配置**：从 `config.yml` 的 `rtsp://` URL 中提取旧 IP，用 `sed` 全局替换为新 IP。
4. **重启服务**：在 Frigate 目录下执行 `sudo docker compose down` 和 `sudo docker compose up -d`。

## 使用方法

```bash
# 1. 将脚本复制到 Linux 机器上（或直接 clone 仓库）
# 2. 添加执行权限
chmod +x update_camera_ip.sh

# 3. 执行脚本（需要 sudo 权限）
sudo ./update_camera_ip.sh
```

## 关键配置项

如需修改以下参数，直接编辑脚本顶部的「配置」区块：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TARGET_MAC` | `f8:ce:21:63:5e:b8` | 摄像头的 MAC 地址 |
| `FRIGATE_DIR` | `/home/gavin/dockercompose/frigate` | Frigate 配置目录 |
| `CONFIG_FILE` | `${FRIGATE_DIR}/config.yml` | Frigate 主配置文件路径 |

## 注意事项

- 脚本通过 `rtsp://` URL 中的 IP 识别旧地址，请确保 `config.yml` 中摄像头流地址使用该格式。
- 每次运行只保留当天日期的备份文件；同一天多次运行会覆盖当天备份。
- 建议配合 cron 定时任务使用，例如每天凌晨检查一次：

  ```cron
  0 3 * * * /path/to/update_camera_ip.sh >> /var/log/update_camera_ip.log 2>&1
  ```
