#!/usr/bin/env python3
"""
EMTEEGEE Beast Laptop Synthesis Runner
====================================
This script should be run on the beast laptop to generate complete analyses.
It will continuously monitor for cards ready for synthesis and process them.
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')

import django
django.setup()

from synthesis_manager import synthesis_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - BEAST-SYNTHESIS - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('beast_synthesis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BeastSynthesisRunner:
    """Automated synthesis runner for the beast laptop."""
    
    def __init__(self):
        self.running = False
        self.batch_size = 3  # Process 3 cards at a time
        self.sleep_interval = 30  # Check every 30 seconds
        self.total_processed = 0
        self.total_success = 0
        self.total_failed = 0
        
    def should_run(self) -> bool:
        """Check if this machine should run synthesis."""
        if not synthesis_manager.should_synthesize_on_this_machine():
            logger.error("❌ This machine is not configured for synthesis!")
            logger.error("   Only the beast laptop should run this script.")
            logger.error(f"   Current hostname: {synthesis_manager.hostname}")
            logger.error("   Expected: hostname containing 'beast'")
            return False
        return True
    
    def run_continuous(self):
        """Run synthesis continuously with monitoring."""
        if not self.should_run():
            return
        
        logger.info("🚀 Starting Beast Laptop Synthesis Runner")
        logger.info(f"   Hostname: {synthesis_manager.hostname}")
        logger.info(f"   Model: {synthesis_manager.model}")
        logger.info(f"   Batch Size: {self.batch_size}")
        logger.info(f"   Check Interval: {self.sleep_interval} seconds")
        logger.info("=" * 60)
        
        self.running = True
        last_stats = None
        
        try:
            while self.running:
                try:
                    # Get current statistics
                    stats = synthesis_manager.get_synthesis_stats()
                    
                    # Log stats if they changed
                    if stats != last_stats:
                        logger.info("📊 Current Statistics:")
                        logger.info(f"   Cards with all components: {stats['cards_with_all_components']}")
                        logger.info(f"   Cards with synthesis: {stats['cards_with_synthesis']}")
                        logger.info(f"   Cards ready for synthesis: {stats['cards_ready_for_synthesis']}")
                        logger.info(f"   Completion rate: {stats['synthesis_completion_rate']}%")
                        last_stats = stats
                    
                    # Check if there's work to do
                    if stats['cards_ready_for_synthesis'] > 0:
                        logger.info(f"🎯 Found {stats['cards_ready_for_synthesis']} cards ready for synthesis")
                        
                        # Run synthesis batch
                        logger.info(f"🤖 Processing batch of {self.batch_size} cards...")
                        results = synthesis_manager.run_synthesis_batch(self.batch_size)
                        
                        # Update totals
                        self.total_processed += results.get('processed', 0)
                        self.total_success += results.get('success', 0)
                        self.total_failed += results.get('failed', 0)
                        
                        # Log results
                        if results.get('success', 0) > 0:
                            logger.info(f"✅ Successfully synthesized {results['success']} analyses")
                        if results.get('failed', 0) > 0:
                            logger.info(f"❌ Failed to synthesize {results['failed']} analyses")
                        
                        # Log session totals
                        logger.info(f"📈 Session Totals: {self.total_success} success, {self.total_failed} failed, {self.total_processed} total processed")
                        
                    else:
                        logger.info("✅ All caught up! No cards ready for synthesis.")
                    
                    # Wait before next check
                    logger.info(f"⏳ Waiting {self.sleep_interval} seconds until next check...")
                    time.sleep(self.sleep_interval)
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Received shutdown signal...")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in synthesis loop: {e}")
                    logger.info("⏳ Waiting 60 seconds before retry...")
                    time.sleep(60)
                    
        finally:
            self.running = False
            logger.info("🏁 Beast Synthesis Runner stopped")
            logger.info(f"📊 Final Session Stats:")
            logger.info(f"   Total Processed: {self.total_processed}")
            logger.info(f"   Total Success: {self.total_success}")
            logger.info(f"   Total Failed: {self.total_failed}")
            if self.total_processed > 0:
                success_rate = (self.total_success / self.total_processed) * 100
                logger.info(f"   Success Rate: {success_rate:.1f}%")
    
    def run_single_batch(self):
        """Run a single synthesis batch."""
        if not self.should_run():
            return
        
        logger.info("🎯 Running single synthesis batch")
        
        # Get stats
        stats = synthesis_manager.get_synthesis_stats()
        logger.info(f"📊 Ready for synthesis: {stats['cards_ready_for_synthesis']} cards")
        
        if stats['cards_ready_for_synthesis'] == 0:
            logger.info("✅ No cards ready for synthesis")
            return
        
        # Run batch
        results = synthesis_manager.run_synthesis_batch(self.batch_size)
        
        # Log results
        logger.info("📈 Batch Results:")
        for key, value in results.items():
            logger.info(f"   {key}: {value}")
        
        if results.get('success', 0) > 0:
            logger.info(f"✅ Successfully generated {results['success']} complete analyses!")

def main():
    """Main entry point with command line options."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Beast Laptop Synthesis Runner')
    parser.add_argument('--continuous', action='store_true', 
                       help='Run continuously, checking for new work every 30 seconds')
    parser.add_argument('--batch-size', type=int, default=3,
                       help='Number of cards to process in each batch (default: 3)')
    parser.add_argument('--interval', type=int, default=30,
                       help='Seconds between checks in continuous mode (default: 30)')
    
    args = parser.parse_args()
    
    runner = BeastSynthesisRunner()
    runner.batch_size = args.batch_size
    runner.sleep_interval = args.interval
    
    if args.continuous:
        logger.info("🔄 Starting continuous synthesis mode")
        runner.run_continuous()
    else:
        logger.info("⚡ Running single batch synthesis")
        runner.run_single_batch()

if __name__ == '__main__':
    main()
