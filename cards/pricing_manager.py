"""
Advanced Pricing Manager for EMTEEGEE
Integrates MTGjson pricing data (90-day history + daily updates) with Scryfall pricing
to provide worl        if should_download_daily:
            logger.info("📅 Downloading current prices (cached file is old or missing)...")
            if self._download_xz_file(self.MTGJSON_TODAY_PRICES, daily_file):
                logger.info("✅ Current pricing updated")
            else:
                logger.error("❌ Failed to download current pricing")s pricing intelligence for MTG cards.

INTELLIGENT CACHING:
- Only downloads once per day (checks file timestamps)
- Uses .xz compression for smallest file sizes
- Caches decompressed data locally
- Respects MTGjson's resources
"""

import logging
import requests
import json
import lzma
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from pymongo import UpdateOne, UpdateMany
import statistics
import os
from .models import get_cards_collection

logger = logging.getLogger(__name__)

class MTGPricingManager:
    """
    Advanced pricing system that merges multiple data sources:
    1. MTGjson pricing data (comprehensive, 90-day history)
    2. Scryfall pricing (real-time, good coverage)
    3. Historical analysis and trend detection
    
    FEATURES:
    - Smart caching: only downloads once per day
    - .xz compression support for smallest files
    - Intelligent file management
    """    # MTGjson pricing endpoints with .xz compression
    MTGJSON_PRICING_BASE = "https://mtgjson.com/api/v5"
    MTGJSON_ALL_PRICES = f"{MTGJSON_PRICING_BASE}/AllPrices.json.xz"  # Contains 90-day history
    MTGJSON_TODAY_PRICES = f"{MTGJSON_PRICING_BASE}/AllPricesToday.json.xz"  # Current day only
    
    # Local cache directories
    PRICING_CACHE_DIR = Path("downloads/pricing")
    
    def __init__(self):
        self.cache_dir = self.PRICING_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cards_collection = get_cards_collection()
        
    def _should_download_file(self, file_path: Path, max_age_hours: int = 24) -> bool:
        """
        Check if a file should be downloaded based on age.
        
        Args:
            file_path: Path to the file to check
            max_age_hours: Maximum age in hours before re-download
            
        Returns:
            True if file should be downloaded
        """
        if not file_path.exists():
            return True
            
        # Check file age
        file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
        return file_age.total_seconds() > (max_age_hours * 3600)
    
    def _get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in MB."""
        if file_path.exists():
            return file_path.stat().st_size / (1024 * 1024)
        return 0.0
    
    def _download_xz_file(self, url: str, output_path: Path) -> bool:
        """
        Download and decompress an .xz file.
        
        Args:
            url: URL to download from
            output_path: Path to save decompressed file
            
        Returns:
            True if successful
        """
        xz_path = output_path.with_suffix(output_path.suffix + '.xz')
        
        try:
            logger.info(f"📥 Downloading {url}...")
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            # Download compressed file
            with open(xz_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            compressed_size = self._get_file_size_mb(xz_path)
            logger.info(f"✅ Downloaded compressed file: {compressed_size:.1f} MB")
            
            # Decompress
            logger.info("🔄 Decompressing .xz file...")
            with lzma.open(xz_path, 'rt', encoding='utf-8') as f:
                data = f.read()
                
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(data)
            
            decompressed_size = self._get_file_size_mb(output_path)
            logger.info(f"✅ Decompressed: {decompressed_size:.1f} MB")
            
            # Clean up compressed file
            xz_path.unlink()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to download/decompress {url}: {e}")
            # Clean up partial files
            for cleanup_path in [xz_path, output_path]:
                if cleanup_path.exists():
                    cleanup_path.unlink()
            return False
    
    def download_mtgjson_pricing(self, include_history: bool = True, force_download: bool = False) -> Dict[str, Any]:
        """
        Download comprehensive pricing data from MTGjson with intelligent caching.
        
        Args:
            include_history: Whether to download 90-day price history
            force_download: Override cache and force download
            
        Returns:
            Dictionary containing pricing data structure
        """
        logger.info("🏷️ MTGjson Pricing Download with Smart Caching")
        
        pricing_data = {}
        
        # Current pricing file paths
        daily_file = self.cache_dir / "mtgjson_daily_prices.json"
        history_file = self.cache_dir / "mtgjson_price_history.json"
        
        # Download current pricing
        should_download_daily = force_download or self._should_download_file(daily_file, 24)
        
        if should_download_daily:
            logger.info("� Downloading current prices (cached file is old or missing)...")
            if self._download_xz_file(self.MTGJSON_DAILY_PRICES, daily_file):
                logger.info("✅ Current pricing updated")
            else:
                logger.error("❌ Failed to download current pricing")
        else:
            age_hours = (datetime.now() - datetime.fromtimestamp(daily_file.stat().st_mtime)).total_seconds() / 3600
            logger.info(f"📋 Using cached current pricing (age: {age_hours:.1f} hours)")
        
        # Load current pricing
        if daily_file.exists():
            try:
                with open(daily_file, 'r', encoding='utf-8') as f:
                    pricing_data['current'] = json.load(f)
                logger.info(f"✅ Loaded current pricing: {len(pricing_data['current'].get('data', {}))} sets")
            except Exception as e:
                logger.error(f"Failed to load current pricing: {e}")
          # Download 90-day history if requested
        if include_history:
            should_download_history = force_download or self._should_download_file(history_file, 24)
            
            if should_download_history:
                logger.info("📈 Downloading 90-day price history (this may take a while)...")
                if self._download_xz_file(self.MTGJSON_ALL_PRICES, history_file):
                    logger.info("✅ Price history updated")
                else:
                    logger.error("❌ Failed to download price history")
            else:
                age_hours = (datetime.now() - datetime.fromtimestamp(history_file.stat().st_mtime)).total_seconds() / 3600
                logger.info(f"📊 Using cached price history (age: {age_hours:.1f} hours)")
            
            # Load price history
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        pricing_data['history'] = json.load(f)
                    logger.info(f"✅ Loaded price history: {len(pricing_data['history'].get('data', {}))} sets")
                except Exception as e:
                    logger.error(f"Failed to load price history: {e}")
        
        # Cache summary
        self._log_cache_summary()
        
        return pricing_data
    
    def _log_cache_summary(self):
        """Log current cache status."""
        logger.info("\n📂 Pricing Cache Status:")
        
        files_to_check = [
            ("Current Prices", "mtgjson_daily_prices.json"),
            ("Price History", "mtgjson_price_history.json"),
        ]
        
        for name, filename in files_to_check:
            file_path = self.cache_dir / filename
            if file_path.exists():
                size_mb = self._get_file_size_mb(file_path)
                age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                age_str = f"{age.days}d {age.seconds//3600}h ago"
                logger.info(f"  📄 {name}: {size_mb:.1f} MB, updated {age_str}")
            else:
                logger.info(f"  ❌ {name}: Not cached")
        
        total_size = sum(
            self._get_file_size_mb(self.cache_dir / filename) 
            for _, filename in files_to_check
            if (self.cache_dir / filename).exists()
        )
        logger.info(f"  💾 Total cache size: {total_size:.1f} MB")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached pricing files.
        
        Returns:
            Dictionary with cache status information
        """
        cache_info = {
            'current_prices': None,
            'price_history': None,
            'total_size_mb': 0,
            'needs_update': False
        }
        
        files = [
            ('current_prices', 'mtgjson_daily_prices.json'),
            ('price_history', 'mtgjson_price_history.json')
        ]
        
        for key, filename in files:
            file_path = self.cache_dir / filename
            if file_path.exists():
                stat = file_path.stat()
                age_hours = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() / 3600
                size_mb = stat.st_size / (1024 * 1024)
                
                cache_info[key] = {
                    'exists': True,
                    'size_mb': round(size_mb, 1),
                    'age_hours': round(age_hours, 1),
                    'needs_update': age_hours > 24,
                    'last_modified': datetime.fromtimestamp(stat.st_mtime)
                }
                
                cache_info['total_size_mb'] += size_mb
                
                if age_hours > 24:
                    cache_info['needs_update'] = True
            else:
                cache_info[key] = {
                    'exists': False,
                    'needs_update': True
                }
        
        cache_info['total_size_mb'] = round(cache_info['total_size_mb'], 1)
        
        return cache_info
    
    def extract_card_pricing(self, pricing_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract and organize pricing data by card UUID.
        
        MTGjson structure:
        {
          "data": {
            "SET_CODE": {
              "CARD_UUID": {
                "paper": {
                  "cardmarket": {"retail": {"2023-01-01": 1.50, ...}, "buylist": {...}},
                  "cardkingdom": {...},
                  "tcgplayer": {...}
                },
                "mtgo": {...},
                "mtgoFoil": {...}
              }
            }
          }
        }
        """
        logger.info("🔍 Extracting card pricing data...")
        
        card_prices = {}
        
        # Process current pricing
        if 'current' in pricing_data:
            current_data = pricing_data['current'].get('data', {})
            
            for set_code, set_data in current_data.items():
                for card_uuid, card_pricing in set_data.items():
                    if card_uuid not in card_prices:
                        card_prices[card_uuid] = {
                            'current': {},
                            'history': [],
                            'sources': set(),
                            'last_updated': datetime.utcnow(),
                            'trend_analysis': {}
                        }
                    
                    # Extract current prices from all sources
                    self._extract_current_prices(card_prices[card_uuid], card_pricing)
        
        # Process historical pricing
        if 'history' in pricing_data:
            history_data = pricing_data['history'].get('data', {})
            
            for set_code, set_data in history_data.items():
                for card_uuid, card_history in set_data.items():
                    if card_uuid in card_prices:
                        self._extract_price_history(card_prices[card_uuid], card_history)
        
        logger.info(f"✅ Extracted pricing for {len(card_prices)} cards")
        return card_prices
    
    def _extract_current_prices(self, card_price_data: Dict[str, Any], card_pricing: Dict[str, Any]):
        """Extract current prices from all available sources."""
        current_prices = card_price_data['current']
        
        # Paper prices
        paper_data = card_pricing.get('paper', {})
        for source, source_data in paper_data.items():
            card_price_data['sources'].add(source)
            
            # Retail prices (what customers pay)
            retail_data = source_data.get('retail', {})
            if retail_data:
                # Get latest date
                latest_date = max(retail_data.keys()) if retail_data else None
                if latest_date and retail_data[latest_date]:
                    current_prices[f'{source}_retail'] = float(retail_data[latest_date])
            
            # Buylist prices (what stores pay)
            buylist_data = source_data.get('buylist', {})
            if buylist_data:
                latest_date = max(buylist_data.keys()) if buylist_data else None
                if latest_date and buylist_data[latest_date]:
                    current_prices[f'{source}_buylist'] = float(buylist_data[latest_date])
        
        # MTGO prices
        mtgo_data = card_pricing.get('mtgo', {})
        if mtgo_data:
            latest_date = max(mtgo_data.keys()) if mtgo_data else None
            if latest_date and mtgo_data[latest_date]:
                current_prices['mtgo'] = float(mtgo_data[latest_date])
        
        # MTGO Foil prices
        mtgo_foil_data = card_pricing.get('mtgoFoil', {})
        if mtgo_foil_data:
            latest_date = max(mtgo_foil_data.keys()) if mtgo_foil_data else None
            if latest_date and mtgo_foil_data[latest_date]:
                current_prices['mtgo_foil'] = float(mtgo_foil_data[latest_date])
    
    def _extract_price_history(self, card_price_data: Dict[str, Any], card_history: Dict[str, Any]):
        """Extract price history for trend analysis."""
        history = card_price_data['history']
        
        # Extract paper price history
        paper_data = card_history.get('paper', {})
        for source, source_data in paper_data.items():
            retail_data = source_data.get('retail', {})
            
            for date_str, price in retail_data.items():
                if price:
                    history.append({
                        'date': datetime.strptime(date_str, '%Y-%m-%d'),
                        'price': float(price),
                        'source': source,
                        'type': 'retail'
                    })
        
        # Sort history by date
        history.sort(key=lambda x: x['date'])
    
    def calculate_price_metrics(self, card_prices: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate advanced pricing metrics for each card.
        """
        logger.info("📊 Calculating advanced pricing metrics...")
        
        for card_uuid, price_data in card_prices.items():
            metrics = {}
            current_prices = price_data['current']
            history = price_data['history']
            
            # Calculate average current price across sources
            if current_prices:
                retail_prices = [p for k, p in current_prices.items() if 'retail' in k and p > 0]
                if retail_prices:
                    metrics['avg_retail_price'] = statistics.mean(retail_prices)
                    metrics['min_retail_price'] = min(retail_prices)
                    metrics['max_retail_price'] = max(retail_prices)
                    metrics['price_spread'] = max(retail_prices) - min(retail_prices)
                
                # Get specific source prices
                metrics['tcgplayer_price'] = current_prices.get('tcgplayer_retail', 0)
                metrics['cardmarket_price'] = current_prices.get('cardmarket_retail', 0)
                metrics['cardkingdom_price'] = current_prices.get('cardkingdom_retail', 0)
                
                # MTGO pricing
                metrics['mtgo_price'] = current_prices.get('mtgo', 0)
                metrics['mtgo_foil_price'] = current_prices.get('mtgo_foil', 0)
            
            # Historical trend analysis
            if len(history) >= 2:
                # Calculate 30-day and 90-day trends
                now = datetime.utcnow()
                thirty_days_ago = now - timedelta(days=30)
                ninety_days_ago = now - timedelta(days=90)
                
                recent_prices = [h['price'] for h in history if h['date'] >= thirty_days_ago]
                older_prices = [h['price'] for h in history if h['date'] >= ninety_days_ago and h['date'] < thirty_days_ago]
                
                if recent_prices and older_prices:
                    recent_avg = statistics.mean(recent_prices)
                    older_avg = statistics.mean(older_prices)
                    
                    metrics['price_trend_30d'] = ((recent_avg - older_avg) / older_avg) * 100
                    metrics['volatility'] = statistics.stdev(recent_prices) if len(recent_prices) > 1 else 0
                
                # Price movement categories
                if metrics.get('price_trend_30d', 0) > 20:
                    metrics['trend_category'] = 'rising_fast'
                elif metrics.get('price_trend_30d', 0) > 5:
                    metrics['trend_category'] = 'rising'
                elif metrics.get('price_trend_30d', 0) < -20:
                    metrics['trend_category'] = 'falling_fast'
                elif metrics.get('price_trend_30d', 0) < -5:
                    metrics['trend_category'] = 'falling'
                else:
                    metrics['trend_category'] = 'stable'
            
            price_data['trend_analysis'] = metrics
        
        logger.info("✅ Calculated pricing metrics for all cards")
        return card_prices
    
    def merge_with_scryfall_pricing(self, card_prices: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Merge MTGjson pricing with existing Scryfall pricing data.
        MTGjson is authoritative for pricing, but Scryfall provides backup.
        """
        logger.info("🔄 Merging MTGjson pricing with Scryfall data...")
        
        # Get cards that have Scryfall pricing
        scryfall_cards = list(self.cards_collection.find(
            {'prices': {'$exists': True}},
            {'uuid': 1, 'prices': 1, 'name': 1}
        ))
        
        scryfall_by_uuid = {card['uuid']: card for card in scryfall_cards}
        
        for card_uuid, mtgjson_data in card_prices.items():
            # If we have Scryfall data for this card, merge it
            if card_uuid in scryfall_by_uuid:
                scryfall_prices = scryfall_by_uuid[card_uuid].get('prices', {})
                
                # Use MTGjson as primary, Scryfall as fallback
                merged_pricing = {
                    # MTGjson pricing (primary)
                    'usd': mtgjson_data['trend_analysis'].get('tcgplayer_price') or 
                           mtgjson_data['trend_analysis'].get('avg_retail_price') or
                           float(scryfall_prices.get('usd', 0)),
                    
                    'eur': mtgjson_data['trend_analysis'].get('cardmarket_price') or
                           float(scryfall_prices.get('eur', 0)),
                    
                    # MTGO pricing from MTGjson
                    'tix': mtgjson_data['trend_analysis'].get('mtgo_price') or
                           float(scryfall_prices.get('tix', 0)),
                    
                    # Foil pricing (Scryfall fallback)
                    'usd_foil': float(scryfall_prices.get('usd_foil', 0)),
                    'eur_foil': float(scryfall_prices.get('eur_foil', 0)),
                    
                    # Advanced pricing from MTGjson
                    'price_sources': {
                        'tcgplayer': mtgjson_data['trend_analysis'].get('tcgplayer_price', 0),
                        'cardmarket': mtgjson_data['trend_analysis'].get('cardmarket_price', 0),
                        'cardkingdom': mtgjson_data['trend_analysis'].get('cardkingdom_price', 0),
                    },
                    
                    # Pricing intelligence
                    'price_trend_30d': mtgjson_data['trend_analysis'].get('price_trend_30d', 0),
                    'trend_category': mtgjson_data['trend_analysis'].get('trend_category', 'unknown'),
                    'volatility': mtgjson_data['trend_analysis'].get('volatility', 0),
                    'price_spread': mtgjson_data['trend_analysis'].get('price_spread', 0),
                    
                    # Data quality indicators
                    'data_sources': list(mtgjson_data['sources']),
                    'last_updated': mtgjson_data['last_updated'],
                    'history_count': len(mtgjson_data['history'])
                }
                
                # Clean up zero values
                merged_pricing = {k: v for k, v in merged_pricing.items() if v != 0 or k in ['price_trend_30d', 'volatility']}
                
                mtgjson_data['merged_pricing'] = merged_pricing
        
        logger.info("✅ Merged MTGjson and Scryfall pricing data")
        return card_prices
    
    def update_card_pricing(self, card_prices: Dict[str, Dict[str, Any]], batch_size: int = 1000) -> Dict[str, int]:
        """
        Update cards in MongoDB with enhanced pricing data.
        """
        logger.info(f"💾 Updating card pricing in database (batch size: {batch_size})...")
        
        update_operations = []
        stats = {'updated': 0, 'errors': 0, 'skipped': 0}
        
        for card_uuid, price_data in card_prices.items():
            if 'merged_pricing' not in price_data:
                stats['skipped'] += 1
                continue
                
            try:
                merged_pricing = price_data['merged_pricing']
                
                # Prepare update operation
                update_operations.append(
                    UpdateOne(
                        {'uuid': card_uuid},
                        {
                            '$set': {
                                'prices': merged_pricing,
                                'pricing_last_updated': datetime.utcnow(),
                                'pricing_source': 'mtgjson_primary'
                            }
                        }
                    )
                )
                
                # Execute batch updates
                if len(update_operations) >= batch_size:
                    result = self.cards_collection.bulk_write(update_operations)
                    stats['updated'] += result.modified_count
                    update_operations = []
                    
            except Exception as e:
                logger.error(f"Error updating pricing for card {card_uuid}: {e}")
                stats['errors'] += 1
        
        # Execute remaining updates
        if update_operations:
            result = self.cards_collection.bulk_write(update_operations)
            stats['updated'] += result.modified_count
        
        logger.info(f"✅ Pricing update complete: {stats}")
        return stats
    
    def get_pricing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of pricing data quality and coverage.
        """
        pipeline = [
            {
                '$match': {
                    'prices': {'$exists': True}
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_with_pricing': {'$sum': 1},
                    'avg_usd_price': {'$avg': '$prices.usd'},
                    'max_usd_price': {'$max': '$prices.usd'},
                    'min_usd_price': {'$min': '$prices.usd'},
                    'mtgjson_sourced': {
                        '$sum': {
                            '$cond': [
                                {'$eq': ['$pricing_source', 'mtgjson_primary']},
                                1, 0
                            ]
                        }
                    }
                }
            }
        ]
        
        result = list(self.cards_collection.aggregate(pipeline))
        
        if result:
            stats = result[0]
            return {
                'total_cards_with_pricing': stats['total_with_pricing'],
                'average_price_usd': round(stats.get('avg_usd_price', 0), 2),
                'highest_price_usd': round(stats.get('max_usd_price', 0), 2),
                'lowest_price_usd': round(stats.get('min_usd_price', 0), 2),
                'mtgjson_sourced': stats.get('mtgjson_sourced', 0),
                'data_quality': stats.get('mtgjson_sourced', 0) / stats['total_with_pricing'] * 100
            }
        
        return {}
    
    def full_pricing_update(self, include_history: bool = True) -> Dict[str, Any]:
        """
        Complete pricing update workflow.
        
        1. Download MTGjson pricing data
        2. Extract and organize pricing by card
        3. Calculate advanced metrics and trends
        4. Merge with existing Scryfall data
        5. Update database
        6. Return comprehensive statistics
        """
        logger.info("🚀 Starting full pricing update workflow...")
        
        try:
            # Step 1: Download MTGjson data
            pricing_data = self.download_mtgjson_pricing(include_history=include_history)
            
            # Step 2: Extract card pricing
            card_prices = self.extract_card_pricing(pricing_data)
            
            # Step 3: Calculate metrics
            card_prices = self.calculate_price_metrics(card_prices)
            
            # Step 4: Merge with Scryfall
            card_prices = self.merge_with_scryfall_pricing(card_prices)
            
            # Step 5: Update database
            update_stats = self.update_card_pricing(card_prices)
            
            # Step 6: Get final summary
            pricing_summary = self.get_pricing_summary()
            
            return {
                'success': True,
                'cards_processed': len(card_prices),
                'update_stats': update_stats,
                'pricing_summary': pricing_summary,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Full pricing update failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow()
            }


def get_pricing_manager() -> MTGPricingManager:
    """Get the singleton pricing manager instance."""
    return MTGPricingManager()
