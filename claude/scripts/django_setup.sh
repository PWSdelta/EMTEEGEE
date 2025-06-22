#!/bin/bash
# Django Application Setup Script
# Run as emteegee user after cloning the repository

set -e

cd /home/emteegee/emteegee

echo "🐍 Setting up Django application..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file from template
echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✏️  Please edit .env file with your settings:"
        echo "   - MongoDB connection string"
        echo "   - Django secret key"
        echo "   - Domain name"
    else
        # Create basic .env template
        cat > .env << EOF
# EMTeeGee Production Environment Variables
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# MongoDB Atlas Connection
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/emteegee?retryWrites=true&w=majority

# API Configuration
DJANGO_API_BASE_URL=https://yourdomain.com

# Ollama Configuration (if running on VPS)
OLLAMA_HOST=http://localhost:11434
EOF
        echo "📝 Created .env template. Please edit with your settings."
    fi
fi

# Generate Django secret key if not set
echo "🔑 Generating Django secret key..."
python3 << EOF
import secrets
import string

# Read current .env
with open('.env', 'r') as f:
    content = f.read()

# Generate new secret key if placeholder exists
if 'your-secret-key-here' in content:
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    secret_key = ''.join(secrets.choice(alphabet) for i in range(50))
    content = content.replace('your-secret-key-here', secret_key)
    
    with open('.env', 'w') as f:
        f.write(content)
    print("✅ Generated new Django secret key")
else:
    print("✅ Django secret key already set")
EOF

# Test Django configuration
echo "🧪 Testing Django configuration..."
python manage.py check

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create necessary directories
echo "📁 Creating log directories..."
mkdir -p logs
mkdir -p static
mkdir -p media

# Set proper permissions
echo "🔒 Setting file permissions..."
chmod 755 /home/emteegee/emteegee
chmod 644 .env

echo "✅ Django application setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your MongoDB connection string"
echo "2. Run: source venv/bin/activate && python manage.py check"
echo "3. Configure Nginx and Gunicorn services"
echo "4. Setup SSL certificate"
echo ""
echo "🎉 Ready for production deployment!"
