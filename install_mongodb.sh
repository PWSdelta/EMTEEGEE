#!/bin/bash
"""
🚀 MONGODB LOCAL INSTALLATION SCRIPT - Ubuntu 22.04
===================================================

This script will:
1. Install MongoDB 7.0 on your Ubuntu 22.04 server
2. Configure it securely
3. Help you migrate from MongoDB Atlas
4. Set up your Django app to use local MongoDB

Run with: chmod +x install_mongodb.sh && ./install_mongodb.sh
"""

set -e  # Exit on any error

echo "🚀 Installing MongoDB on Ubuntu 22.04..."
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update

# Import MongoDB public GPG key
echo "🔑 Adding MongoDB GPG key..."
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Add MongoDB repository
echo "📋 Adding MongoDB repository..."
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package list
echo "🔄 Updating package list..."
sudo apt update

# Install MongoDB
echo "⬇️  Installing MongoDB..."
sudo apt install -y mongodb-org

# Start and enable MongoDB
echo "🚀 Starting MongoDB service..."
sudo systemctl start mongod
sudo systemctl enable mongod

# Check status
echo "✅ Checking MongoDB status..."
sudo systemctl status mongod --no-pager

# Create MongoDB data directory with proper permissions
echo "📁 Setting up MongoDB directories..."
sudo mkdir -p /var/lib/mongodb
sudo chown mongodb:mongodb /var/lib/mongodb

# Configure MongoDB for production
echo "⚙️  Configuring MongoDB..."
sudo tee /etc/mongod.conf > /dev/null << 'EOF'
# mongod.conf - MongoDB configuration file

# Storage settings
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

# Network settings  
net:
  port: 27017
  bindIp: 127.0.0.1

# Process management
processManagement:
  fork: true
  pidFilePath: /var/run/mongodb/mongod.pid

# Logging
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

# Security (optional - uncomment if you want authentication)
# security:
#   authorization: enabled
EOF

# Restart MongoDB with new config
echo "🔄 Restarting MongoDB with new configuration..."
sudo systemctl restart mongod

# Test MongoDB connection
echo "🧪 Testing MongoDB connection..."
if mongosh --eval "db.runCommand('ping').ok" emteegee_dev --quiet; then
    echo "✅ MongoDB is running successfully!"
else
    echo "❌ MongoDB connection test failed"
    exit 1
fi

# Display connection info
echo ""
echo "🎉 MongoDB Installation Complete!"
echo "=================================="
echo "MongoDB is now running on: localhost:27017"
echo "Database created: emteegee_dev"
echo ""
echo "📋 Next Steps:"
echo "1. Export your data from MongoDB Atlas"
echo "2. Import data to local MongoDB"
echo "3. Update Django settings"
echo ""
echo "💾 Data Migration Commands:"
echo "# Export from Atlas (run from your local machine):"
echo "mongodump --uri='mongodb+srv://username:password@cluster.mongodb.net/emteegee_dev'"
echo ""
echo "# Import to local MongoDB (run on this server):"
echo "mongorestore --db emteegee_dev dump/emteegee_dev/"
echo ""
echo "🔧 Django Settings Update:"
echo "Update your Django settings to use: 'mongodb://localhost:27017/'"
echo ""
echo "🔍 MongoDB Management:"
echo "# Connect to MongoDB shell:"
echo "mongosh emteegee_dev"
echo ""
echo "# Check service status:"
echo "sudo systemctl status mongod"
echo ""
echo "# View logs:"
echo "sudo tail -f /var/log/mongodb/mongod.log"
echo ""
echo "🎯 Your MTG card analysis system will now run without Atlas limits!"
