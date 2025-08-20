#!/bin/bash

# Install Chrome on Render
set -e

echo "Installing Chrome dependencies..."
apt-get update
apt-get install -y wget gnupg

echo "Downloading and installing Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

echo "Checking Chrome version..."
google-chrome-stable --version

echo "Chrome installation completed!"
