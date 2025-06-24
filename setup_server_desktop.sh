#!/bin/bash
"""
Server Desktop Setup Script
Sets up minimal desktop environment + VS Code for remote development
"""

set -e  # Exit on error

echo "🖥️  Setting up minimal desktop environment + VS Code"
echo "=" * 55

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install minimal desktop environment (XFCE)
echo "🖼️  Installing XFCE desktop environment..."
sudo apt install -y xfce4 xfce4-goodies

# Install remote access options
echo "🔗 Installing remote access tools..."
sudo apt install -y x2goserver x2goserver-xsession
sudo apt install -y tightvncserver  # Backup option

# Install VS Code
echo "💻 Installing Visual Studio Code..."
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
sudo apt update
sudo apt install -y code

# Install essential development tools
echo "🛠️  Installing development tools..."
sudo apt install -y git curl wget nano vim htop tree
sudo apt install -y build-essential python3-dev python3-pip
sudo apt install -y firefox-esr  # Lightweight browser

# Install MongoDB tools (for GUI management)
echo "🗄️  Installing MongoDB tools..."
sudo apt install -y mongodb-clients
# Optional: MongoDB Compass (GUI)
wget https://downloads.mongodb.com/compass/mongodb-compass_1.43.0_amd64.deb
sudo dpkg -i mongodb-compass_1.43.0_amd64.deb || sudo apt-get install -f -y

# Set up X2Go for remote access
echo "🌐 Configuring X2Go..."
sudo systemctl enable x2goserver
sudo systemctl start x2goserver

# Create desktop shortcuts for your project
echo "🔗 Creating desktop shortcuts..."
mkdir -p ~/Desktop

cat > ~/Desktop/EMTEEGEE-Project.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=EMTEEGEE Project
Comment=Open EMTEEGEE project in VS Code
Exec=code ~/emteegee
Icon=code
Terminal=false
Categories=Development;
EOF

cat > ~/Desktop/MongoDB-Dashboard.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=MongoDB Dashboard
Comment=Open EMTEEGEE dashboard
Exec=firefox http://localhost:8000/cards/dashboard/
Icon=firefox
Terminal=false
Categories=Development;
EOF

chmod +x ~/Desktop/*.desktop

# Install useful VS Code extensions
echo "🧩 Installing VS Code extensions..."
code --install-extension ms-python.python
code --install-extension ms-python.pylint
code --install-extension ms-vscode.vscode-json
code --install-extension bradlc.vscode-tailwindcss
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension formulahendry.auto-rename-tag

# Configure VS Code settings for your project
echo "⚙️  Configuring VS Code..."
mkdir -p ~/.config/Code/User
cat > ~/.config/Code/User/settings.json << EOF
{
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "python.terminal.activateEnvironment": true,
    "editor.fontSize": 14,
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000,
    "terminal.integrated.shell.linux": "/bin/bash",
    "workbench.colorTheme": "Default Dark+",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "mongodb.connectionSaving": "Workspace"
}
EOF

# Set up firewall rules for remote access
echo "🔒 Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 2222/tcp  # X2Go
sudo ufw allow 5901/tcp  # VNC (if needed)
sudo ufw --force enable

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 Next steps:"
echo "1. Reboot the server: sudo reboot"
echo "2. Install X2Go client on your Windows machine"
echo "3. Connect to your server using X2Go:"
echo "   - Host: your-server-ip"
echo "   - Login: your-username"
echo "   - Session type: XFCE"
echo "   - Port: 22"
echo ""
echo "📁 Your EMTEEGEE project will be at: ~/emteegee"
echo "🖥️  VS Code will be available in the applications menu"
echo "🌐 Dashboard shortcut will be on the desktop"
echo ""
echo "Alternative VNC access:"
echo "Run: vncserver :1 -geometry 1920x1080 -depth 24"
echo "Then connect to: your-server-ip:5901"
