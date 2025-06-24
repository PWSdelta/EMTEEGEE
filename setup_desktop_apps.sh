#!/bin/bash
"""
Desktop Applications Setup Script
Run this AFTER you have a desktop environment running
"""

set -e  # Exit on error

echo "💻 Installing desktop applications..."
echo "=" * 40

# Install VS Code (now that we have a desktop)
echo "🔧 Installing Visual Studio Code..."
# Clean up any previous conflicting installations
sudo rm -f /etc/apt/sources.list.d/vscode.list
sudo rm -f /etc/apt/trusted.gpg.d/packages.microsoft.gpg
sudo rm -f /usr/share/keyrings/microsoft.gpg

# Install VS Code properly
curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
sudo apt update
sudo apt install -y code

# Install web browser
echo "🌐 Installing Firefox..."
sudo apt install -y firefox-esr

# Install MongoDB tools
echo "🗄️  Installing MongoDB tools..."
sudo apt install -y mongodb-clients

# Optional: MongoDB Compass (GUI)
echo "📊 Installing MongoDB Compass..."
wget https://downloads.mongodb.com/compass/mongodb-compass_1.43.0_amd64.deb
sudo dpkg -i mongodb-compass_1.43.0_amd64.deb || sudo apt-get install -f -y
rm -f mongodb-compass_1.43.0_amd64.deb

# Create desktop shortcuts
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

# Install VS Code extensions
echo "🧩 Installing VS Code extensions..."
code --install-extension ms-python.python
code --install-extension ms-python.pylint
code --install-extension ms-vscode.vscode-json
code --install-extension bradlc.vscode-tailwindcss

# Configure VS Code
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
    "python.linting.pylintEnabled": true
}
EOF

# Set up firewall
echo "🔒 Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 2222/tcp  # X2Go
sudo ufw allow 5901/tcp  # VNC
sudo ufw --force enable

echo ""
echo "🎉 ALL APPLICATIONS INSTALLED!"
echo ""
echo "✅ You now have:"
echo "   - VS Code with Python extensions"
echo "   - Firefox browser"
echo "   - MongoDB Compass"
echo "   - Desktop shortcuts for your EMTEEGEE project"
echo ""
echo "🚀 Ready to develop!"
