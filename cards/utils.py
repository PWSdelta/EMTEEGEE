from datetime import datetime, timedelta
from .models import get_cards_collection

def get_home_page_stats():
    """Get statistics for the home page stats blocks"""
    collection = get_cards_collection()
    
    # Total Cards (you already have this working)
    total_cards = collection.count_documents({})
    
    # Fully Analyzed - cards with complete analysis (synthesis)
    fully_analyzed = collection.count_documents({
        "complete_analysis": {"$exists": True, "$ne": ""}
    })
    
    # In Process - cards with components assigned to workers
    in_process = collection.count_documents({
        "analysis.components": {"$exists": True, "$ne": {}}
    })
    
    # Analyzed Today - cards with components generated today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Count cards that have been analyzed today
    analyzed_today = collection.count_documents({
        "$or": [
            {
                "analysis.last_updated": {
                    "$gte": today_start,
                    "$lt": today_end
                }
            },
            {
                "complete_analysis_metadata.generated_at": {
                    "$gte": today_start,
                    "$lt": today_end
                }
            }
        ]
    })
    
    return {
        'total_cards': total_cards,
        'fully_analyzed': fully_analyzed,
        'in_process': in_process,
        'analyzed_today': analyzed_today
    }

def get_recent_cards_with_analysis(limit=60):
    """Get recent cards with analysis for home page display"""
    collection = get_cards_collection()
    
    # Get cards with analysis, sorted by most recent analysis
    cards = list(collection.find({
        "analysis.components": {"$exists": True, "$ne": {}}
    }).sort([
        ("complete_analysis_metadata.generated_at", -1),
        ("analysis.last_updated", -1),
        ("_id", -1)
    ]).limit(limit))
    
    return cards
