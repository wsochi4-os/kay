#!/bin/bash

# Download Ubuntu bootstrap for Kutti
# This script downloads a minimal Ubuntu rootfs for use with proot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default architecture
ARCH="${1:-aarch64}"

# Ubuntu version
UBUNTU_VERSION="22.04"

# Download URL
echo "Downloading Ubuntu $UBUNTU_VERSION rootfs for $ARCH..."

case "$ARCH" in
    aarch64)
        URL="https://github.com/termux/proot-distro/releases/download/v1.1.0/ubuntu-rootfs-arm64.tar.gz"
        ;;
    x86_64)
        URL="https://github.com/termux/proot-distro/releases/download/v1.1.0/ubuntu-rootfs-amd64.tar.gz"
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        echo "Supported architectures: aarch64, x86_64"
        exit 1
        ;;
esac

# Output file
OUTPUT_FILE="$PROJECT_ROOT/packages/android/app/src/main/assets/bootstrap-$ARCH.tar.gz"

# Create assets directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/packages/android/app/src/main/assets"

# Download the file
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Downloading to: $OUTPUT_FILE"
    curl -L "$URL" -o "$OUTPUT_FILE"
    echo "Download complete!"
else
    echo "File already exists: $OUTPUT_FILE"
fi

# Verify the file
if [ -f "$OUTPUT_FILE" ]; then
    FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE")
    echo "File size: $FILE_SIZE bytes"
    echo "Ubuntu bootstrap downloaded successfully!"
else
    echo "Download failed!"
    exit 1
fi
