# Server Desktop Setup Guide

## Quick Setup

1. **Copy setup script to your server:**
   ```bash
   scp setup_server_desktop.sh user@your-server:/home/user/
   ```

2. **Run the setup script on your server:**
   ```bash
   ssh user@your-server
   chmod +x setup_server_desktop.sh
   ./setup_server_desktop.sh
   ```

3. **Reboot the server:**
   ```bash
   sudo reboot
   ```

## Windows Client Setup (X2Go - Recommended)

1. **Download X2Go Client:**
   - Go to: https://wiki.x2go.org/doku.php/download:start
   - Download "X2Go Client for Windows"
   - Install it

2. **Configure X2Go Connection:**
   - Open X2Go Client
   - Click "New Session"
   - Fill in:
     - **Session name:** EMTEEGEE Server
     - **Host:** your-server-ip-address
     - **Login:** your-username
     - **SSH port:** 22
     - **Session type:** XFCE
   - Click OK

3. **Connect:**
   - Double-click your session
   - Enter your password
   - You'll see the XFCE desktop!

## Alternative: VNC Setup

If X2Go doesn't work, use VNC:

1. **On the server, start VNC:**
   ```bash
   vncserver :1 -geometry 1920x1080 -depth 24
   ```

2. **On Windows, install VNC Viewer:**
   - Download from RealVNC or TightVNC
   - Connect to: `your-server-ip:5901`

## What You'll Have

- **XFCE Desktop Environment** - Lightweight and familiar
- **VS Code** - Full-featured, ready for Python/Django development
- **MongoDB Compass** - GUI for database management
- **Firefox** - For testing your web apps
- **Desktop Shortcuts** - Quick access to your EMTEEGEE project
- **Pre-configured VS Code Extensions:**
  - Python support
  - Pylint linting
  - JSON support
  - Tailwind CSS (for your frontend)

## Your Workflow

1. **Connect via X2Go** - Get full desktop experience
2. **Open VS Code** - Your EMTEEGEE project will be ready
3. **Open Terminal in VS Code** - Run your workers and scripts
4. **Open Firefox** - Monitor your dashboard at `localhost:8000`
5. **Use MongoDB Compass** - Manage your database visually

## Performance Tips

- **Set resolution appropriately** - Don't go higher than your client screen
- **Close unused applications** - Keep memory usage reasonable
- **Use VS Code's integrated terminal** - Instead of separate terminal windows

## Troubleshooting

**If X2Go won't connect:**
- Check firewall: `sudo ufw status`
- Check X2Go service: `sudo systemctl status x2goserver`
- Try VNC as backup

**If VS Code is slow:**
- Disable heavy extensions
- Reduce editor font size
- Use "code --disable-gpu" if needed

**If you need more performance:**
- Switch to i3wm instead of XFCE
- Use SSH + X11 forwarding for just VS Code: `ssh -X user@server code`

## Ready to Go!

Once set up, you'll have a full development environment on your server with:
- Direct access to your MongoDB
- Real-time worker monitoring
- Instant script testing
- No more git push/pull cycles for quick fixes!
