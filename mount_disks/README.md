# mount_disks

这个目录放的是你这台 mini 主机上三块盘的一键挂载脚本。

## 对应关系

- `lenovo`：`bc014ec9-458e-4a44-aeee-3b9c53256ca9`，挂载到 `/mnt/lenovo`
- `u12tdisk`：`67D4-3357`，挂载到 `/mnt/u12tdisk`
- `u10tdisk`：`663C-D732`，挂载到 `/mnt/u10tdisk`

脚本会优先按 UUID 找设备，再自动创建挂载目录。
`exfat` 盘会使用 `TARGET_USER` 对应的 `uid/gid` 挂载，默认是 `gavin`。

## 用法

先给脚本执行权限：

```bash
chmod +x mount_disks.sh
```

常用命令：

```bash
sudo ./mount_disks.sh all
sudo ./mount_disks.sh status
sudo ./mount_disks.sh umount
```

如果 `exfat` 盘的目标用户不是 `gavin`，可以这样指定：

```bash
TARGET_USER=yourname sudo ./mount_disks.sh all
```

## 说明

- `all`：依次挂载三块盘
- `lenovo`：只挂载 `lenovo`
- `u12t`：只挂载 `u12tdisk`
- `u10t`：只挂载 `u10tdisk`
- `status`：查看当前挂载状态
- `umount`：卸载这三块盘

## 依赖

- `mount`
- `umount`
- `blkid`
- `exfat` 支持（系统已安装 exfat 工具）
