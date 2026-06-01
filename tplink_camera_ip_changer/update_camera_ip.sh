#!/usr/bin/env bash
# update_camera_ip.sh
# 自动查找摄像头 MAC 对应的 IP，更新 Frigate 配置并重启服务

set -euo pipefail

# ─── 配置 ────────────────────────────────────────────────────────────────────
TARGET_MAC="f8:ce:21:63:5e:b8"
FRIGATE_DIR="/home/gavin/dockercompose/frigate"
CONFIG_FILE="${FRIGATE_DIR}/config.yml"
# ─────────────────────────────────────────────────────────────────────────────

echo "[1/4] 正在局域网中查找 MAC 地址: ${TARGET_MAC} ..."

# 刷新 ARP 表（发送一次广播 ping，忽略结果）
ping -c 1 -b "$(ip route | awk '/default/{print $3}' | sed 's/\.[0-9]*$/.255/')" \
    &>/dev/null || true

# 先尝试 ip neigh，再回退到 arp -n
NEW_IP=$(ip neigh 2>/dev/null \
    | awk -v mac="${TARGET_MAC}" 'tolower($5) == tolower(mac) {print $1; exit}')

if [[ -z "${NEW_IP}" ]]; then
    NEW_IP=$(arp -n 2>/dev/null \
        | awk -v mac="${TARGET_MAC}" 'tolower($3) == tolower(mac) {print $1; exit}')
fi

if [[ -z "${NEW_IP}" ]]; then
    echo "[ERROR] 未在 ARP 表中找到 MAC 地址 ${TARGET_MAC} 对应的设备，脚本退出。" >&2
    exit 1
fi

echo "        发现设备 IP: ${NEW_IP}"

# ─── 提取 config.yml 中当前摄像头的旧 IP ────────────────────────────────────
echo "[2/4] 备份配置文件 ..."

if [[ ! -f "${CONFIG_FILE}" ]]; then
    echo "[ERROR] 配置文件不存在: ${CONFIG_FILE}" >&2
    exit 1
fi

DATE_TAG=$(date +%m%d)
BACKUP_FILE="${FRIGATE_DIR}/config_${DATE_TAG}.yml"
cp "${CONFIG_FILE}" "${BACKUP_FILE}"
echo "        已备份至: ${BACKUP_FILE}"

# ─── 提取旧 IP（取 config.yml 中 rtsp:// 行里第一个 IPv4 地址作为旧 IP）──────
OLD_IP=$(grep -oP '(?<=rtsp://)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "${CONFIG_FILE}" \
    | head -n 1)

if [[ -z "${OLD_IP}" ]]; then
    echo "[ERROR] 无法从 ${CONFIG_FILE} 中提取旧 IP 地址（未找到 rtsp:// 行）。" >&2
    exit 1
fi

if [[ "${OLD_IP}" == "${NEW_IP}" ]]; then
    echo "        当前 IP (${OLD_IP}) 与新 IP 相同，无需修改配置。"
else
    echo "[3/4] 将配置中的旧 IP ${OLD_IP} 替换为新 IP ${NEW_IP} ..."
    sed -i "s/${OLD_IP}/${NEW_IP}/g" "${CONFIG_FILE}"
    echo "        配置已更新。"
fi

# ─── 重启 Frigate ─────────────────────────────────────────────────────────────
echo "[4/4] 重启 Frigate 容器 ..."
cd "${FRIGATE_DIR}"

echo "        执行: sudo docker compose down"
sudo docker compose down

echo "        执行: sudo docker compose up -d"
sudo docker compose up -d

echo ""
echo "✓ 完成。Frigate 已使用新 IP ${NEW_IP} 重启。"
