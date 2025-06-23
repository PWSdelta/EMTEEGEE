#!/bin/bash
"""
📦 MONGODB ATLAS TO LOCAL MIGRATION SCRIPT
==========================================

This script helps you migrate your data from MongoDB Atlas to your local MongoDB.
Run AFTER installing MongoDB locally.

Usage: ./migrate_from_atlas.sh "your-atlas-connection-string"
"""

set -e

ATLAS_URI="$1"
LOCAL_DB="emteegee_dev"
BACKUP_DIR="./atlas_backup"

if [ -z "$ATLAS_URI" ]; then
    echo "❌ Error: Please provide your Atlas connection string"
    echo ""
    echo "Usage: $0 'mongodb+srv://username:password@cluster.mongodb.net/emteegee_dev'"
    echo ""
    echo "🔍 Find your Atlas connection string in:"
    echo "   Atlas Dashboard > Connect > Connect your application"
    exit 1
fi

echo "📦 Migrating data from MongoDB Atlas to local MongoDB..."
echo "======================================================="

# Create backup directory
echo "📁 Creating backup directory..."
mkdir -p "$BACKUP_DIR"

# Export data from Atlas
echo "⬇️  Exporting data from Atlas..."
echo "This may take a few minutes for 29K cards..."
mongodump --uri="$ATLAS_URI" --out="$BACKUP_DIR"

# Check if export was successful
if [ ! -d "$BACKUP_DIR/$LOCAL_DB" ]; then
    echo "❌ Export failed - no data directory found"
    echo "Check your Atlas connection string and try again"
    exit 1
fi

# Show what was exported
echo "✅ Export complete! Collections found:"
ls -la "$BACKUP_DIR/$LOCAL_DB/"

# Import to local MongoDB
echo ""
echo "⬆️  Importing data to local MongoDB..."
mongorestore --db "$LOCAL_DB" "$BACKUP_DIR/$LOCAL_DB/"

# Verify import
echo ""
echo "🧪 Verifying migration..."
CARD_COUNT=$(mongosh "$LOCAL_DB" --eval "db.cards.countDocuments({})" --quiet)
echo "Cards imported: $CARD_COUNT"

if [ "$CARD_COUNT" -gt 25000 ]; then
    echo "✅ Migration successful! $CARD_COUNT cards imported"
else
    echo "⚠️  Warning: Only $CARD_COUNT cards imported (expected ~29,000)"
fi

# Show collection stats
echo ""
echo "📊 Collection Statistics:"
mongosh "$LOCAL_DB" --eval "
    const collections = db.getCollectionNames();
    collections.forEach(col => {
        const count = db[col].countDocuments();
        print(\`\${col}: \${count} documents\`);
    });
" --quiet

echo ""
echo "🎉 Migration Complete!"
echo "====================="
echo "Your MongoDB Atlas data is now available locally at:"
echo "mongodb://localhost:27017/$LOCAL_DB"
echo ""
echo "🔧 Next: Update your Django settings to use local MongoDB"
echo "🗑️  Cleanup: You can delete $BACKUP_DIR when everything works"
echo ""
echo "🚀 Your swarm system can now load 29K cards without Atlas limits!"
