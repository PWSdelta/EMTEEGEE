"""
Enhanced Swarm Monitoring Configuration
Configure monitoring thresholds, alerts, and performance targets
"""

from datetime import timedelta
from typing import Dict, Any, List

class MonitoringConfig:
    """Configuration for performance monitoring and alerting"""
    
    # Performance thresholds
    PERFORMANCE_THRESHOLDS = {
        'worker_task_time_warning_seconds': 300,  # 5 minutes
        'worker_task_time_critical_seconds': 600,  # 10 minutes
        'worker_idle_warning_minutes': 15,
        'worker_offline_critical_minutes': 30,
        'system_tasks_per_hour_minimum': 10,
        'completion_rate_warning_percentage': 85,
        'completion_rate_critical_percentage': 70,
        'queue_size_warning': 100,
        'queue_size_critical': 500
    }
    
    # Monitoring intervals
    MONITORING_INTERVALS = {
        'metrics_collection_seconds': 30,
        'dashboard_refresh_seconds': 10,
        'alert_check_seconds': 60,
        'performance_report_minutes': 15,
        'historical_cleanup_hours': 24
    }
    
    # Alert configuration
    ALERT_CONFIG = {
        'enabled': True,
        'console_alerts': True,
        'log_alerts': True,
        'email_alerts': False,  # Configure SMTP settings if needed
        'webhook_alerts': False  # Configure webhook URL if needed
    }
    
    # Performance targets
    PERFORMANCE_TARGETS = {
        'cards_per_hour_target': 50,
        'components_per_hour_target': 1000,
        'worker_efficiency_target_percentage': 90,
        'system_uptime_target_percentage': 99,
        'average_task_time_target_seconds': 120
    }
    
    # Dashboard configuration
    DASHBOARD_CONFIG = {
        'port': 8888,
        'host': 'localhost',
        'auto_refresh_seconds': 10,
        'history_points': 100,
        'worker_details_expanded': True,
        'show_performance_targets': True
    }
    
    @classmethod
    def get_alert_conditions(cls) -> List[Dict[str, Any]]:
        """Get list of alert conditions to monitor"""
        return [
            {
                'name': 'Worker Offline',
                'description': 'Worker has been offline for more than 30 minutes',
                'severity': 'critical',
                'condition': lambda metrics: any(
                    worker['status'] == 'offline' 
                    for worker in metrics['worker_performance']['worker_details'].values()
                )
            },
            {
                'name': 'High Queue Size',
                'description': 'Task queue has grown beyond threshold',
                'severity': 'warning',
                'condition': lambda metrics: (
                    metrics['task_completion']['queue_status']['pending_tasks'] > 
                    cls.PERFORMANCE_THRESHOLDS['queue_size_warning']
                )
            },
            {
                'name': 'Low Completion Rate',
                'description': 'Task completion rate has dropped below threshold',
                'severity': 'warning',
                'condition': lambda metrics: (
                    metrics['task_completion']['period_metrics']['last_hour']['completion_rate_percentage'] < 
                    cls.PERFORMANCE_THRESHOLDS['completion_rate_warning_percentage']
                )
            },
            {
                'name': 'Slow Task Processing',
                'description': 'Average task time has exceeded threshold',
                'severity': 'warning',
                'condition': lambda metrics: (
                    metrics['worker_performance']['average_system_task_time'] > 
                    cls.PERFORMANCE_THRESHOLDS['worker_task_time_warning_seconds']
                )
            },
            {
                'name': 'Low System Throughput',
                'description': 'System throughput has dropped below minimum',
                'severity': 'critical',
                'condition': lambda metrics: (
                    metrics['throughput']['last_hour']['cards_per_hour'] < 
                    cls.PERFORMANCE_THRESHOLDS['system_tasks_per_hour_minimum']
                )
            }
        ]
    
    @classmethod
    def evaluate_performance_against_targets(cls, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate current performance against configured targets"""
        targets = cls.PERFORMANCE_TARGETS
        
        # Calculate performance scores
        throughput_score = min(100, (
            metrics['throughput']['last_hour']['cards_per_hour'] / 
            targets['cards_per_hour_target'] * 100
        ))
        
        component_score = min(100, (
            metrics['throughput']['last_hour']['components_per_hour'] / 
            targets['components_per_hour_target'] * 100
        ))
        
        efficiency_score = 100 - min(100, (
            metrics['worker_performance']['average_system_task_time'] / 
            targets['average_task_time_target_seconds'] * 100
        ))
        
        overall_score = (throughput_score + component_score + efficiency_score) / 3
        
        return {
            'overall_performance_score': round(overall_score, 1),
            'throughput_performance': {
                'score': round(throughput_score, 1),
                'target': targets['cards_per_hour_target'],
                'actual': metrics['throughput']['last_hour']['cards_per_hour'],
                'status': 'good' if throughput_score >= 80 else 'warning' if throughput_score >= 60 else 'critical'
            },
            'component_performance': {
                'score': round(component_score, 1),
                'target': targets['components_per_hour_target'],
                'actual': metrics['throughput']['last_hour']['components_per_hour'],
                'status': 'good' if component_score >= 80 else 'warning' if component_score >= 60 else 'critical'
            },
            'efficiency_performance': {
                'score': round(efficiency_score, 1),
                'target': targets['average_task_time_target_seconds'],
                'actual': metrics['worker_performance']['average_system_task_time'],
                'status': 'good' if efficiency_score >= 80 else 'warning' if efficiency_score >= 60 else 'critical'
            }
        }

# Global configuration instance
monitoring_config = MonitoringConfig()