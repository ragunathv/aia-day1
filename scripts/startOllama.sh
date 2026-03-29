#!/usr/bin/env bash
set -euo pipefail

# ---- Ensure prerequisites ----
install_zstd() {
  if command -v zstd >/dev/null 2>&1; then
    echo "zstd already installed"
    return
  fi

  echo "Installing zstd..."

  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y
    sudo apt-get install -y zstd curl ca-certificates
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y zstd curl ca-certificates
  elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y zstd curl ca-certificates
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm zstd curl ca-certificates
  else
    echo "ERROR: Unsupported package manager. Install 'zstd' manually and rerun."
    exit 1
  fi
}
