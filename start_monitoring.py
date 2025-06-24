#!/usr/bin/env python3
"""
Enhanced Swarm Monitoring Launcher
Start performance monitoring with various options
"""

import sys
import argparse
from performance_monitor import PerformanceMonitor
from performance_dashboard import start_dashboard_server
import threading

def main():
    parser = argparse.ArgumentParser(description='Enhanced Swarm Performance Monitoring')
    parser.add_argument('--mode', choices=['report', 'monitor', 'dashboard', 'both'], 
                       default='report', help='Monitoring mode')
    parser.add_argument('--interval', type=int, default=30, 
                       help='Monitoring interval in seconds')
    parser.add_argument('--port', type=int, default=8888, 
                       help='Dashboard port')
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor()
    
    if args.mode == 'report':
        # Generate single report
        print("📊 Generating Performance Report...")
        report = monitor.generate_performance_report()
        print(report)
        
    elif args.mode == 'monitor':
        # Continuous monitoring
        print(f"🔄 Starting continuous monitoring (interval: {args.interval}s)")
        monitor.monitor_continuously(args.interval)
        
    elif args.mode == 'dashboard':
        # Web dashboard only
        print(f"🌐 Starting web dashboard on port {args.port}")
        start_dashboard_server(args.port)
        
    elif args.mode == 'both':
        # Both monitoring and dashboard
        print(f"🚀 Starting both monitoring and dashboard")
        
        # Start dashboard in separate thread
        dashboard_thread = threading.Thread(
            target=start_dashboard_server, 
            args=(args.port,),
            daemon=True
        )
        dashboard_thread.start()
        
        # Start monitoring in main thread
        print(f"🔄 Starting continuous monitoring (interval: {args.interval}s)")
        monitor.monitor_continuously(args.interval)

if __name__ == "__main__":
    main()