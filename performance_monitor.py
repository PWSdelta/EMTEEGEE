# Create performance_monitor.py
#!/usr/bin/env python3
"""
Enhanced Swarm Performance Monitor
Real-time monitoring of worker throughput and task completion rates
"""

import os
import django
import time
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm
from cards.swarm_logging import enhanced_swarm_logger

class PerformanceMonitor:
    """Real-time performance monitoring for the enhanced swarm system"""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.task_completion_history = deque(maxlen=history_size)
        self.worker_performance_history = defaultdict(lambda: deque(maxlen=history_size))
        self.system_metrics_history = deque(maxlen=history_size)
        self.start_time = datetime.now(timezone.utc)
        
    def collect_real_time_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive real-time performance metrics"""
        current_time = datetime.now(timezone.utc)
        
        # Basic system status
        status = enhanced_swarm.get_enhanced_swarm_status()
        
        # Worker performance metrics
        worker_metrics = self._get_worker_performance_metrics()
        
        # Task completion metrics
        task_metrics = self._get_task_completion_metrics()
        
        # System throughput metrics
        throughput_metrics = self._get_throughput_metrics()
        
        # Card analysis progress
        analysis_progress = self._get_analysis_progress_metrics()
        
        metrics = {
            'timestamp': current_time,
            'system_status': status,
            'worker_performance': worker_metrics,
            'task_completion': task_metrics,
            'throughput': throughput_metrics,
            'analysis_progress': analysis_progress,
            'uptime_seconds': (current_time - self.start_time).total_seconds()
        }
        
        # Store in history
        self.system_metrics_history.append(metrics)
        
        return metrics
    
    def _get_worker_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed worker performance metrics"""
        # Get active workers
        active_workers = list(enhanced_swarm.workers.find({
            'status': 'active',
            'last_heartbeat': {'$gte': datetime.now(timezone.utc) - timedelta(minutes=5)}
        }))
        
        # Get recent task completions (last hour)
        recent_tasks = list(enhanced_swarm.tasks.find({
            'status': 'completed',
            'completed_at': {'$gte': datetime.now(timezone.utc) - timedelta(hours=1)}
        }).sort('completed_at', -1))
        
        # Calculate per-worker metrics
        worker_stats = {}
        for worker in active_workers:
            worker_id = worker['worker_id']
            worker_tasks = [t for t in recent_tasks if t.get('assigned_to') == worker_id]
            
            # Fix timezone handling for last_heartbeat
            last_heartbeat = worker['last_heartbeat']
            if last_heartbeat.tzinfo is None:
                last_heartbeat = last_heartbeat.replace(tzinfo=timezone.utc)
            
            # Calculate time difference safely
            now = datetime.now(timezone.utc)
            time_diff_seconds = (now - last_heartbeat).total_seconds()
            
            # Determine worker status
            if time_diff_seconds < 300:  # 5 minutes
                worker_status = 'active'
            elif time_diff_seconds < 1800:  # 30 minutes
                worker_status = 'stale'
            else:
                worker_status = 'offline'
            
            if worker_tasks:
                # Calculate average task time
                execution_times = []
                for task in worker_tasks:
                    if 'created_at' in task and 'completed_at' in task:
                        # Handle timezone for task timestamps too
                        created_at = task['created_at']
                        completed_at = task['completed_at']
                        
                        if created_at.tzinfo is None:
                            created_at = created_at.replace(tzinfo=timezone.utc)
                        if completed_at.tzinfo is None:
                            completed_at = completed_at.replace(tzinfo=timezone.utc)
                        
                        duration = (completed_at - created_at).total_seconds()
                        execution_times.append(duration)
                
                avg_task_time = sum(execution_times) / len(execution_times) if execution_times else 0
                tasks_per_hour = len(worker_tasks)
                
                worker_stats[worker_id] = {
                    'tasks_completed_last_hour': tasks_per_hour,
                    'average_task_time_seconds': round(avg_task_time, 2),
                    'tasks_per_hour_rate': round(tasks_per_hour, 2),
                    'last_heartbeat': last_heartbeat,
                    'total_tasks_completed': worker.get('tasks_completed', 0),
                    'capabilities': worker.get('capabilities', {}),
                    'status': worker_status
                }
            else:
                worker_stats[worker_id] = {
                    'tasks_completed_last_hour': 0,
                    'average_task_time_seconds': 0,
                    'tasks_per_hour_rate': 0,
                    'last_heartbeat': last_heartbeat,
                    'total_tasks_completed': worker.get('tasks_completed', 0),
                    'capabilities': worker.get('capabilities', {}),
                    'status': worker_status
                }
        
        # Calculate system average task time with timezone fixes
        system_execution_times = []
        for task in recent_tasks:
            if 'created_at' in task and 'completed_at' in task:
                created_at = task['created_at']
                completed_at = task['completed_at']
                
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                if completed_at.tzinfo is None:
                    completed_at = completed_at.replace(tzinfo=timezone.utc)
                
                duration = (completed_at - created_at).total_seconds()
                system_execution_times.append(duration)
        
        return {
            'active_workers': len(active_workers),
            'worker_details': worker_stats,
            'total_tasks_last_hour': len(recent_tasks),
            'average_system_task_time': round(sum(system_execution_times) / len(system_execution_times), 2) if system_execution_times else 0
        }
    
    def _get_task_completion_metrics(self) -> Dict[str, Any]:
        """Get task completion rate and timing metrics"""
        now = datetime.now(timezone.utc)
        
        # Task completion over different time periods
        periods = {
            'last_5_minutes': timedelta(minutes=5),
            'last_15_minutes': timedelta(minutes=15),
            'last_hour': timedelta(hours=1),
            'last_6_hours': timedelta(hours=6),
            'last_24_hours': timedelta(days=1)
        }
        
        completion_metrics = {}
        for period_name, period_delta in periods.items():
            since_time = now - period_delta
            
            completed_tasks = enhanced_swarm.tasks.count_documents({
                'status': 'completed',
                'completed_at': {'$gte': since_time}
            })
            
            failed_tasks = enhanced_swarm.tasks.count_documents({
                'status': 'failed',
                'completed_at': {'$gte': since_time}
            })
            
            total_period_tasks = completed_tasks + failed_tasks
            completion_rate = (completed_tasks / total_period_tasks * 100) if total_period_tasks > 0 else 0
            
            completion_metrics[period_name] = {
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'completion_rate_percentage': round(completion_rate, 1),
                'tasks_per_minute': round(completed_tasks / (period_delta.total_seconds() / 60), 2)
            }
        
        # Current queue status
        pending_tasks = enhanced_swarm.tasks.count_documents({'status': 'assigned'})
        assigned_tasks = enhanced_swarm.tasks.count_documents({'status': 'assigned'})
        
        return {
            'period_metrics': completion_metrics,
            'queue_status': {
                'pending_tasks': pending_tasks,
                'assigned_tasks': assigned_tasks,
                'estimated_completion_time_minutes': round(
                    pending_tasks / (completion_metrics['last_hour']['tasks_per_minute'] or 1), 2
                ) if completion_metrics['last_hour']['tasks_per_minute'] > 0 else 'unknown'
            }
        }
    
    def _get_throughput_metrics(self) -> Dict[str, Any]:
        """Get system throughput metrics"""
        # Cards analyzed over time
        now = datetime.now(timezone.utc)
        
        # Cards completed in different periods
        periods = {
            'last_hour': timedelta(hours=1),
            'last_6_hours': timedelta(hours=6),
            'last_24_hours': timedelta(days=1)
        }
        
        throughput_metrics = {}
        for period_name, period_delta in periods.items():
            since_time = now - period_delta
            
            cards_completed = enhanced_swarm.cards.count_documents({
                'analysis.analysis_completed_at': {'$gte': since_time}
            })
            
            components_generated = enhanced_swarm.tasks.count_documents({
                'status': 'completed',
                'completed_at': {'$gte': since_time}
            }) * 20  # Assuming 20 components per task
            
            throughput_metrics[period_name] = {
                'cards_completed': cards_completed,
                'components_generated': components_generated,
                'cards_per_hour': round(cards_completed / (period_delta.total_seconds() / 3600), 2),
                'components_per_hour': round(components_generated / (period_delta.total_seconds() / 3600), 2)
            }
        
        return throughput_metrics
    
    def _get_analysis_progress_metrics(self) -> Dict[str, Any]:
        """Get card analysis progress metrics"""
        # Total progress
        total_cards = enhanced_swarm.cards.count_documents({})
        fully_analyzed = enhanced_swarm.cards.count_documents({
            'analysis.fully_analyzed': True
        })
        partially_analyzed = enhanced_swarm.cards.count_documents({
            'analysis.component_count': {'$gt': 0, '$lt': 20}
        })
        not_analyzed = total_cards - fully_analyzed - partially_analyzed
        
        # Progress by card categories
        high_priority_analyzed = enhanced_swarm.cards.count_documents({
            'edhrecRank': {'$lte': 1000},
            'analysis.fully_analyzed': True
        })
        high_priority_total = enhanced_swarm.cards.count_documents({
            'edhrecRank': {'$lte': 1000}
        })
        
        return {
            'total_progress': {
                'total_cards': total_cards,
                'fully_analyzed': fully_analyzed,
                'partially_analyzed': partially_analyzed,
                'not_analyzed': not_analyzed,
                'completion_percentage': round((fully_analyzed / total_cards * 100), 2) if total_cards > 0 else 0
            },
            'high_priority_progress': {
                'analyzed': high_priority_analyzed,
                'total': high_priority_total,
                'completion_percentage': round((high_priority_analyzed / high_priority_total * 100), 2) if high_priority_total > 0 else 0
            },
            'estimated_completion': {
                'remaining_cards': not_analyzed + partially_analyzed,
                'current_rate_cards_per_hour': self._calculate_current_completion_rate(),
                'estimated_hours_to_completion': self._estimate_completion_time()
            }
        }
    
    def _calculate_current_completion_rate(self) -> float:
        """Calculate current card completion rate per hour"""
        now = datetime.now(timezone.utc)
        last_hour = now - timedelta(hours=1)
        
        cards_completed_last_hour = enhanced_swarm.cards.count_documents({
            'analysis.analysis_completed_at': {'$gte': last_hour}
        })
        
        return round(cards_completed_last_hour, 2)
    
    def _estimate_completion_time(self) -> Optional[float]:
        """Estimate time to complete all remaining cards"""
        current_rate = self._calculate_current_completion_rate()
        if current_rate <= 0:
            return None
        
        total_cards = enhanced_swarm.cards.count_documents({})
        fully_analyzed = enhanced_swarm.cards.count_documents({
            'analysis.fully_analyzed': True
        })
        remaining = total_cards - fully_analyzed
        
        return round(remaining / current_rate, 1) if current_rate > 0 else None
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report"""
        metrics = self.collect_real_time_metrics()
        
        report = []
        report.append("🚀 ENHANCED SWARM PERFORMANCE REPORT")
        report.append("=" * 60)
        
        # System overview
        status = metrics['system_status']
        report.append(f"\n📊 SYSTEM OVERVIEW")
        report.append(f"   Active Workers: {status['workers']['active']}/{status['workers']['total']}")
        report.append(f"   Pending Tasks: {status['tasks']['pending']}")
        report.append(f"   Completed Tasks: {status['tasks']['completed']}")
        report.append(f"   Cards Analyzed: {status['cards']['analyzed']}/{status['cards']['total']} ({status['cards']['completion_rate']})")
        report.append(f"   System Uptime: {round(metrics['uptime_seconds']/3600, 1)} hours")
        
        # Worker performance
        worker_perf = metrics['worker_performance']
        report.append(f"\n👥 WORKER PERFORMANCE")
        report.append(f"   Total Tasks (Last Hour): {worker_perf['total_tasks_last_hour']}")
        report.append(f"   Average Task Time: {worker_perf['average_system_task_time']}s")
        
        for worker_id, stats in worker_perf['worker_details'].items():
            report.append(f"   🔧 {worker_id}:")
            report.append(f"      Status: {stats['status']}")
            report.append(f"      Tasks/Hour: {stats['tasks_per_hour_rate']}")
            report.append(f"      Avg Time: {stats['average_task_time_seconds']}s")
            report.append(f"      Total Completed: {stats['total_tasks_completed']}")
        
        # Throughput metrics
        throughput = metrics['throughput']
        report.append(f"\n⚡ THROUGHPUT METRICS")
        for period, data in throughput.items():
            report.append(f"   {period.replace('_', ' ').title()}:")
            report.append(f"      Cards: {data['cards_completed']} ({data['cards_per_hour']}/hr)")
            report.append(f"      Components: {data['components_generated']} ({data['components_per_hour']}/hr)")
        
        # Progress metrics
        progress = metrics['analysis_progress']
        report.append(f"\n📈 ANALYSIS PROGRESS")
        total_prog = progress['total_progress']
        report.append(f"   Overall: {total_prog['completion_percentage']}% complete")
        report.append(f"   Fully Analyzed: {total_prog['fully_analyzed']:,}")
        report.append(f"   Partially Analyzed: {total_prog['partially_analyzed']:,}")
        report.append(f"   Not Started: {total_prog['not_analyzed']:,}")
        
        high_pri = progress['high_priority_progress']
        report.append(f"   High Priority (Top 1000): {high_pri['completion_percentage']}% complete")
        
        est = progress['estimated_completion']
        if est['estimated_hours_to_completion']:
            report.append(f"   Estimated Completion: {est['estimated_hours_to_completion']} hours")
        else:
            report.append(f"   Estimated Completion: Unable to calculate")
        
        return "\n".join(report)
    
    def monitor_continuously(self, interval_seconds: int = 30):
        """Continuously monitor and report performance"""
        print("🔄 Starting continuous performance monitoring...")
        print(f"📊 Reporting every {interval_seconds} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            iteration = 0
            while True:
                iteration += 1
                
                # Clear screen (optional)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Generate and display report
                report = self.generate_performance_report()
                print(f"Update #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(report)
                
                # Also log to swarm logger
                metrics = self.collect_real_time_metrics()
                enhanced_swarm_logger.info(f"Performance metrics collected: {json.dumps({
                    'active_workers': metrics['worker_performance']['active_workers'],
                    'tasks_per_hour': metrics['throughput']['last_hour']['cards_per_hour'],
                    'completion_percentage': metrics['analysis_progress']['total_progress']['completion_percentage']
                }, default=str)}")
                
                # Wait for next iteration
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")

def main():
    """Main monitoring function"""
    monitor = PerformanceMonitor()
    
    # Generate initial report
    print("📊 Initial Performance Report:")
    print("=" * 60)
    report = monitor.generate_performance_report()
    print(report)
    
    # Ask user if they want continuous monitoring
    response = input("\n🔄 Start continuous monitoring? (y/n): ").strip().lower()
    if response == 'y':
        monitor.monitor_continuously()
    else:
        print("✅ One-time report complete")

if __name__ == "__main__":
    main()