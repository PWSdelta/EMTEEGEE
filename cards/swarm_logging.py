"""
Standardized Logging Configuration for EMTEEGEE Swarm System
Provides consistent, readable logging across all swarm components
"""

import logging
import sys
from datetime import datetime
from typing import Optional

class SwarmFormatter(logging.Formatter):
    """Custom formatter for swarm logging with emojis and structured output"""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[96m',    # Cyan
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    # Emojis for different log levels
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    
    def format(self, record):
        # Add emoji and color
        emoji = self.EMOJIS.get(record.levelname, '📝')
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Create component identifier
        component = getattr(record, 'component', 'SWARM')
        worker_id = getattr(record, 'worker_id', None)
        
        if worker_id:
            identifier = f"{component}[{worker_id[-8:]}]"  # Last 8 chars of worker ID
        else:
            identifier = component
        
        # Format the message
        formatted_msg = f"{color}{emoji} {timestamp} {identifier:>15} | {record.getMessage()}{reset}"
        
        # Add exception info if present
        if record.exc_info:
            formatted_msg += f"\n{self.formatException(record.exc_info)}"
        
        return formatted_msg

class SwarmLogger:
    """Centralized logger for swarm operations"""
    
    def __init__(self, component_name: str, worker_id: Optional[str] = None):
        self.component_name = component_name
        self.worker_id = worker_id
        self.logger = logging.getLogger(f"swarm.{component_name}")
        
        # Configure logger if not already configured
        if not self.logger.handlers:
            self._configure_logger()
    
    def _configure_logger(self):
        """Configure the logger with proper handlers and formatting"""
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(SwarmFormatter())
        
        # File handler for detailed logs
        file_handler = logging.FileHandler('logs/swarm.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s'
        ))
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def _log_with_context(self, level: str, message: str, **kwargs):
        """Log with swarm context"""
        extra = {
            'component': self.component_name,
            'worker_id': self.worker_id,
            **kwargs
        }
        getattr(self.logger, level.lower())(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_with_context('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_with_context('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_with_context('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log_with_context('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_with_context('CRITICAL', message, **kwargs)
    
    def task_started(self, task_id: str, card_name: str, components: list):
        """Log task start"""
        self.info(f"Task started: {card_name} | Components: {', '.join(components)}", 
                 task_id=task_id)
    
    def task_completed(self, task_id: str, card_name: str, execution_time: float, coherence_warnings: int = 0):
        """Log task completion"""
        warning_text = f" | {coherence_warnings} coherence warnings" if coherence_warnings > 0 else ""
        self.info(f"Task completed: {card_name} | {execution_time:.2f}s{warning_text}", 
                 task_id=task_id)
    
    def task_failed(self, task_id: str, card_name: str, error: str):
        """Log task failure"""
        self.error(f"Task failed: {card_name} | Error: {error}", task_id=task_id)
    
    def priority_cache_updated(self, card_count: int):
        """Log priority cache update"""
        self.info(f"Priority cache updated with {card_count:,} cards")
    
    def worker_registered(self, worker_id: str, capabilities: dict):
        """Log worker registration"""
        gpu = "GPU" if capabilities.get('gpu_available') else "CPU"
        ram = capabilities.get('ram_gb', 'Unknown')
        self.info(f"Worker registered: {gpu} | {ram}GB RAM", worker_id=worker_id)
    
    def batch_created(self, batch_size: int, group_key: str, priority_score: float):
        """Log batch creation"""
        self.debug(f"Batch created: {batch_size} cards | Group: {group_key} | Priority: {priority_score:.3f}")
    
    def coherence_warning(self, component: str, conflicts: list):
        """Log coherence warning"""
        self.warning(f"Coherence warning: {component} | Conflicts: {len(conflicts)}")
    
    def stats(self, **metrics):
        """Log system statistics"""
        stats_parts = []
        for key, value in metrics.items():
            if isinstance(value, float):
                stats_parts.append(f"{key}: {value:.2f}")
            elif isinstance(value, int):
                stats_parts.append(f"{key}: {value:,}")
            else:
                stats_parts.append(f"{key}: {value}")
        
        self.info(f"Stats | {' | '.join(stats_parts)}")

# Global logger instances for different components
def get_swarm_logger(component: str, worker_id: Optional[str] = None) -> SwarmLogger:
    """Get a swarm logger for a specific component"""
    return SwarmLogger(component, worker_id)

# Pre-configured loggers for common components
enhanced_swarm_logger = get_swarm_logger('ENHANCED_SWARM')
coherence_logger = get_swarm_logger('COHERENCE')
worker_logger = get_swarm_logger('WORKER')
