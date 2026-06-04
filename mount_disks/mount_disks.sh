#!/usr/bin/env bash

set -euo pipefail

TARGET_USER="${TARGET_USER:-gavin}"

usage() {
  cat <<'EOF'
Usage:
  mount_disks.sh [all|lenovo|u12t|u10t|status|umount]

Environment:
  TARGET_USER   User name used for exfat uid/gid ownership (default: gavin)
EOF
}

info() {
  printf '[%s] %s\n' "$1" "$2"
}

die() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    exec sudo -E -- "$0" "$@"
  fi
}

device_by_uuid() {
  local uuid="$1"

  if command -v blkid >/dev/null 2>&1; then
    blkid -U "$uuid" 2>/dev/null || true
  fi
}

mount_one() {
  local name="$1"
  local uuid="$2"
  local fstype="$3"
  local mountpoint="$4"
  local device

  device="$(device_by_uuid "$uuid")"
  [[ -n "$device" ]] || die "cannot find device for UUID $uuid"

  mkdir -p "$mountpoint"

  if mountpoint -q "$mountpoint"; then
    info "$name" "already mounted at $mountpoint"
    return 0
  fi

  case "$fstype" in
    ext4)
      mount -t ext4 "$device" "$mountpoint"
      ;;
    exfat)
      local uid gid
      uid="$(id -u "$TARGET_USER")"
      gid="$(id -g "$TARGET_USER")"
      mount -t exfat "$device" "$mountpoint" -o "uid=$uid,gid=$gid"
      ;;
    *)
      die "unsupported filesystem type: $fstype"
      ;;
  esac

  info "$name" "mounted $device -> $mountpoint"
}

umount_one() {
  local name="$1"
  local mountpoint="$2"

  if mountpoint -q "$mountpoint"; then
    umount "$mountpoint"
    info "$name" "unmounted $mountpoint"
  else
    info "$name" "not mounted"
  fi
}

status_one() {
  local name="$1"
  local uuid="$2"
  local mountpoint="$3"
  local device

  device="$(device_by_uuid "$uuid")"
  if mountpoint -q "$mountpoint"; then
    info "$name" "mounted at $mountpoint"
    findmnt -n -o SOURCE,TARGET,FSTYPE "$mountpoint"
  else
    info "$name" "not mounted, device=${device:-unknown}, mountpoint=$mountpoint"
  fi
}

main() {
  local action="${1:-all}"

  case "$action" in
    -h|--help|help)
      usage
      ;;
    all)
      require_root "$@"
      mount_one "lenovo" "bc014ec9-458e-4a44-aeee-3b9c53256ca9" "ext4" "/mnt/lenovo"
      mount_one "u12tdisk" "67D4-3357" "exfat" "/mnt/u12tdisk"
      mount_one "u10tdisk" "663C-D732" "exfat" "/mnt/u10tdisk"
      ;;
    lenovo)
      require_root "$@"
      mount_one "lenovo" "bc014ec9-458e-4a44-aeee-3b9c53256ca9" "ext4" "/mnt/lenovo"
      ;;
    u12t)
      require_root "$@"
      mount_one "u12tdisk" "67D4-3357" "exfat" "/mnt/u12tdisk"
      ;;
    u10t)
      require_root "$@"
      mount_one "u10tdisk" "663C-D732" "exfat" "/mnt/u10tdisk"
      ;;
    umount)
      require_root "$@"
      umount_one "u10tdisk" "/mnt/u10tdisk"
      umount_one "u12tdisk" "/mnt/u12tdisk"
      umount_one "lenovo" "/mnt/lenovo"
      ;;
    status)
      status_one "lenovo" "bc014ec9-458e-4a44-aeee-3b9c53256ca9" "/mnt/lenovo"
      status_one "u12tdisk" "67D4-3357" "/mnt/u12tdisk"
      status_one "u10tdisk" "663C-D732" "/mnt/u10tdisk"
      ;;
    *)
      usage
      die "unknown action: $action"
      ;;
  esac
}

main "$@"