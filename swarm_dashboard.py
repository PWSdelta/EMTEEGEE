#!/usr/bin/env python3
"""
Swarm Management Dashboard
Monitor and control the distributed AI analysis system
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from swarm_manager import SwarmManager

class SwarmDashboard:
    """Management interface for the swarm system"""
    
    def __init__(self):
        self.swarm = SwarmManager()
    
    def display_status(self):
        """Display comprehensive swarm status"""
        print("\n" + "="*60)
        print("🐝 AI ANALYSIS SWARM DASHBOARD")
        print("="*60)
        
        status = self.swarm.get_swarm_status()
        
        # Workers section
        print(f"\n📟 WORKERS:")
        print(f"   Total: {status['workers']['total']}")
        print(f"   Active: {status['workers']['active']}")
        
        # Tasks section
        print(f"\n⚡ TASKS:")
        print(f"   Pending: {status['tasks']['pending']}")
        print(f"   Completed: {status['tasks']['completed']}")
        
        # Cards section
        print(f"\n🃏 CARDS:")
        print(f"   Total: {status['cards']['total']:,}")
        print(f"   Analyzed: {status['cards']['analyzed']:,}")
        print(f"   Completion: {status['cards']['completion_rate']}")
        
        # Worker details
        workers = list(self.swarm.workers.find({'status': 'active'}))
        if workers:
            print(f"\n👷 ACTIVE WORKERS:")
            for worker in workers:
                worker_type = worker['capabilities'].get('worker_type', 'unknown')
                ram_gb = worker['capabilities'].get('ram_gb', 0)
                gpu = "🔥 GPU" if worker['capabilities'].get('gpu_available') else "🧠 CPU"
                completed = worker.get('tasks_completed', 0)
                
                last_seen = worker.get('last_heartbeat', datetime.utcnow())
                if isinstance(last_seen, str):
                    last_seen = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                
                time_diff = datetime.utcnow() - last_seen.replace(tzinfo=None)
                status_emoji = "✅" if time_diff < timedelta(minutes=5) else "⚠️"
                
                print(f"   {status_emoji} {worker['worker_id'][:20]:20} | {worker_type:8} | {gpu} | {ram_gb:3}GB | {completed:4} tasks")
    
    def show_recent_completions(self, limit=5):
        """Show recently completed tasks"""
        print(f"\n🏆 RECENT COMPLETIONS (last {limit}):")
        
        recent_tasks = list(self.swarm.tasks.find(
            {'status': 'completed'}
        ).sort('completed_at', -1).limit(limit))
        
        for task in recent_tasks:
            card_name = task.get('card_name', 'Unknown')[:25]
            worker = task.get('assigned_to', 'Unknown')[:15]
            components = len(task.get('components', []))
            exec_time = task.get('execution_time', 0)
            
            print(f"   📝 {card_name:25} | {worker:15} | {components} components | {exec_time:.1f}s")
    
    def show_queue_status(self):
        """Show current queue status"""
        print(f"\n📋 QUEUE STATUS:")
        
        # Count cards needing different types of work
        total_cards = self.swarm.cards.count_documents({})
        needs_analysis = self.swarm.cards.count_documents({
            'analysis.fully_analyzed': {'$ne': True}
        })
        
        # Component completion stats
        component_stats = {}
        for component in self.swarm.GPU_COMPONENTS + self.swarm.CPU_HEAVY_COMPONENTS + self.swarm.BALANCED_COMPONENTS:
            count = self.swarm.cards.count_documents({
                f'analysis.components.{component}': {'$exists': True}
            })
            component_stats[component] = count
        
        print(f"   Cards needing analysis: {needs_analysis:,} / {total_cards:,}")
        print(f"   Component completion rates:")
        
        for component, count in sorted(component_stats.items()):
            percentage = (count / total_cards * 100) if total_cards > 0 else 0
            bar_length = int(percentage / 5)  # Scale to 20 chars max
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"     {component:20} {bar} {percentage:5.1f}% ({count:5,})")
    
    def run_interactive(self):
        """Run interactive dashboard"""
        while True:
            try:
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
                
                self.display_status()
                self.show_recent_completions()
                self.show_queue_status()
                
                print(f"\n🎛️  CONTROLS:")
                print("   [R] Refresh  [Q] Quit  [W] Worker Details")
                
                choice = input("\nChoice: ").upper()
                
                if choice == 'Q':
                    break
                elif choice == 'W':
                    self.show_worker_details()
                    input("\nPress Enter to continue...")
                elif choice == 'R':
                    continue
                else:
                    # Auto-refresh every 5 seconds if no input
                    import time
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                break
        
        print("\n👋 Dashboard closed")
    
    def show_worker_details(self):
        """Show detailed worker information"""
        print(f"\n📊 DETAILED WORKER STATUS:")
        
        workers = list(self.swarm.workers.find({'status': 'active'}))
        
        for worker in workers:
            print(f"\n🤖 {worker['worker_id']}")
            print(f"   Type: {worker['capabilities'].get('worker_type', 'unknown')}")
            print(f"   Platform: {worker['capabilities'].get('platform', 'unknown')}")
            print(f"   CPU Cores: {worker['capabilities'].get('cpu_cores', 0)}")
            print(f"   RAM: {worker['capabilities'].get('ram_gb', 0)} GB")
            print(f"   GPU: {'Yes' if worker['capabilities'].get('gpu_available') else 'No'}")
            print(f"   Tasks Completed: {worker.get('tasks_completed', 0)}")
            print(f"   Tasks Failed: {worker.get('tasks_failed', 0)}")
            
            # Current assignments
            current_tasks = self.swarm.tasks.count_documents({
                'assigned_to': worker['worker_id'],
                'status': 'assigned'
            })
            print(f"   Current Tasks: {current_tasks}")

if __name__ == "__main__":
    dashboard = SwarmDashboard()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        dashboard.run_interactive()
    else:
        dashboard.display_status()
        dashboard.show_recent_completions()
        dashboard.show_queue_status()
