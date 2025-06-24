#!/bin/bash
"""
Server Desktop Setup Script - Fixed Order
Sets up desktop environment FIRST, then GUI applications
"""

set -e  

echo "🖥️  Setting up server desktop environment (logical order)"
echo "=" * 60


echo "📦 Updating system packages..." && \
sudo apt update && sudo apt upgrade -y && \
\
echo "🖼️  Installing XFCE desktop environment..." && \
sudo apt install -y xfce4 xfce4-goodies lightdm && \
\
echo "🚀 Enabling desktop environment..." && \
sudo systemctl enable lightdm && \
\
echo "🔗 Installing remote access tools..." && \
sudo apt install -y x2goserver x2goserver-xsession && \
sudo apt install -y tightvncserver && \
\
echo "🔧 Starting X2Go service..." && \
sudo systemctl enable x2goserver && \
sudo systemctl start x2goserver && \
\
echo "🛠️  Installing development tools..." && \
sudo apt install -y git curl wget nano vim htop tree && \
sudo apt install -y build-essential python3-dev python3-pip && \
\
echo "🖥️  Starting desktop environment..." && \
sudo systemctl start lightdm

echo ""
echo "✅ DESKTOP SETUP COMPLETE!"
echo ""
echo "🎯 Next steps:"
echo "1. You should now see a graphical login screen"
echo "2. Log in with your regular credentials"
echo "3. Once in the desktop, run: ./setup_desktop_apps.sh"
echo ""
echo "🔌 Remote access ready:"
echo "   - X2Go: Connect to port 22 (SSH), session type XFCE"
echo "   - VNC: Run 'vncserver :1' if needed"
echo ""
