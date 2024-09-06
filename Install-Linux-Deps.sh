#!/bin/bash

#####################################################################################
# Install Packages and Command line programs without knowing the distro ahead of time
# Of course this doesn't support all linux distros but it has the popular ones
# @author jredfox
#####################################################################################

# Detect the package manager and install the package
if command -v apt-get &> /dev/null; then
    PKG_MNG="apt"
    echo "sudo apt-get update"
    sudo apt-get update
elif command -v dnf &> /dev/null; then
    PKG_MNG="dnf"
elif command -v yum &> /dev/null; then
    PKG_MNG="yum"
elif command -v zypper &> /dev/null; then
    PKG_MNG="zypper"
elif command -v pacman &> /dev/null; then
    PKG_MNG="pacman"
elif command -v apk &> /dev/null; then
    PKG_MNG="apk"
elif command -v emerge &> /dev/null; then
    PKG_MNG="emerge"
elif command -v equo &> /dev/null; then
    PKG_MNG="entropy"
    echo "sudo eix-sync"
    sudo eix-sync  # Update Entropy database
elif command -v flatpak &> /dev/null; then
    PKG_MNG="flatpak"
elif command -v snap &> /dev/null; then
    PKG_MNG="snap"
elif command -v nix-env &> /dev/null; then
    PKG_MNG="nix"
elif command -v guix &> /dev/null; then
    PKG_MNG="guix"
elif command -v brew &> /dev/null; then
    PKG_MNG="brew"
else
    echo "No supported package manager found."
    exit 1
fi

install_pgk() {
    local package_manager="$1"
    local package_name="$2"
    
    echo "PKG Manager: $package_manager is Installing $package_name"
    
    case "$package_manager" in
        "apt")
            sudo apt-get install -y "$package_name"
            ;;
        "dnf")
            sudo dnf install -y "$package_name"
            ;;
        "yum")
            sudo yum install -y "$package_name"
            ;;
        "zypper")
            sudo zypper install -y "$package_name"
            ;;
        "pacman")
            sudo pacman -Syu --noconfirm "$package_name"
            ;;
        "apk")
            sudo apk add "$package_name"
            ;;
        "emerge")
            sudo emerge "$package_name"
            ;;
        "flatpak")
            flatpak install -y "$package_name"
            ;;
        "snap")
            sudo snap install "$package_name"
            ;;
        "nix")
            nix-env -iA "$package_name"
            ;;
        "guix")
            guix install "$package_name"
            ;;
        "brew")
            brew install "$package_name"
            ;;
        *)
            echo "Unsupported package manager: $package_manager"
            ;;
    esac
}

echo "PKG Manager: $PKG_MNG"

#Handle debian distros
if [[ "$PKG_MNG" == "apt" ]]; then
    for pkg in jq build-essential libssl-dev zlib1g-dev libncurses-dev libgdbm-dev liblzma-dev; do
        if ! dpkg -s "$pkg" > /dev/null 2>&1; then
            install_pgk "$PKG_MNG" "$pkg"
        fi
    done
else
    for pkg in jq build-essential libssl-dev zlib1g-dev libncurses-dev libgdbm-dev liblzma-dev; do
        install_pgk "$PKG_MNG" "$pkg"
    done
fi
