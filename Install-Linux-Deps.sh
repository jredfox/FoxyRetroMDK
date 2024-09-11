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
    echo "sudo dnf check-update"
    sudo dnf check-update
elif command -v yum &> /dev/null; then
    PKG_MNG="yum"
    echo "sudo yum check-update"
    sudo yum check-update
elif command -v zypper &> /dev/null; then
    PKG_MNG="zypper"
    echo "sudo zypper refresh"
    sudo zypper refresh
elif command -v pacman &> /dev/null; then
    PKG_MNG="pacman"
    echo "sudo pacman -Syy"
    sudo pacman -Syy
elif command -v apk &> /dev/null; then
    PKG_MNG="apk"
    echo "sudo apk update"
    sudo apk update
elif command -v emerge &> /dev/null; then
    PKG_MNG="emerge"
    echo "sudo emerge --sync"
    sudo emerge --sync
elif command -v equo &> /dev/null; then
    PKG_MNG="entropy"
    echo "equo update"
    sudo equo update
elif command -v flatpak &> /dev/null; then
    PKG_MNG="flatpak"
    echo "sudo flatpak update --appstream"
    sudo flatpak update --appstream
elif command -v snap &> /dev/null; then
    PKG_MNG="snap"
    echo "sudo snap refresh"
    sudo snap refresh
elif command -v nix-env &> /dev/null; then
    PKG_MNG="nix"
    echo "nix-channel --update"
    nix-channel --update
elif command -v guix &> /dev/null; then
    PKG_MNG="guix"
    echo "guix pull"
    guix pull
elif command -v brew &> /dev/null; then
    PKG_MNG="brew"
    brew update
else
    echo "No supported package manager found."
    exit 1
fi

#Set Flags
#Make Homebrew work
export NONINTERACTIVE=1

install_pkg() {
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
            sudo apk add --no-cache "$package_name"
            ;;
        "emerge")
            sudo emerge --quiet-build "$package_name"
            ;;
        "flatpak")
            flatpak install -y "$package_name"
            ;;
        "snap")
            sudo snap install "$package_name" --yes
            ;;
        "nix")
            nix-env -iA "$package_name"
            ;;
        "guix")
            guix install "$package_name" --yes
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
            install_pkg "$PKG_MNG" "$pkg"
        fi
    done
else
    for pkg in jq build-essential libssl-dev zlib1g-dev libncurses-dev libgdbm-dev liblzma-dev; do
        install_pkg "$PKG_MNG" "$pkg"
    done
fi
