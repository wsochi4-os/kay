#!/bin/bash

# Kutti Bootstrap Script
# This script sets up the Ubuntu environment inside proot

set -e

echo "Starting Kutti Ubuntu bootstrap..."

# Update package lists
echo "Updating package lists..."
apt-get update -y

# Install essential packages
echo "Installing essential packages..."
apt-get install -y \
    curl \
    wget \
    git \
    nodejs \
    npm \
    python3 \
    python3-pip \
    openjdk-17-jdk \
    build-essential \
    sudo \
    less \
    nano \
    htop \
    tmux \
    neofetch

# Set up Node.js (if needed)
echo "Setting up Node.js..."
npm install -g npx pnpm yarn

# Install Kutti CLI
echo "Installing Kutti CLI..."
npm install -g @kutti/cli

# Set up Kutti user
echo "Setting up Kutti user environment..."
USER_HOME="/home/kutti"
mkdir -p "$USER_HOME/.kutti"
mkdir -p "$USER_HOME/.npm"
mkdir -p "$USER_HOME/.config"

# Create .bashrc additions
cat >> "$USER_HOME/.bashrc" << 'EOF'

# Kutti additions
export PATH="$HOME/.npm-global/bin:$PATH"
export KUTTI_CONFIG_DIR="$HOME/.kutti"

# Aliases
alias kutti="kutti"
EOF

# Initialize Kutti
echo "Initializing Kutti..."
kutti init

# Set up npm global prefix
echo "prefix = $USER_HOME/.npm-global" > "$USER_HOME/.npmrc"

# Clean up
echo "Cleaning up..."
apt-get clean
rm -rf /var/lib/apt/lists/*

echo ""
echo "Kutti Ubuntu bootstrap complete!"
echo ""
echo "Welcome to Kutti!"
echo "Type 'kutti --help' to get started."
echo ""
