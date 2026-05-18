#!/usr/bin/env python3
"""
Health Check Script for Vengeance Bot
"""

import sys
import json
import socket
import requests
import psutil
import sqlite3
from datetime import datetime

def check_database():
    """Check database connectivity"""
    try:
        conn = sqlite3.connect('.vengeance/vengeance.db')
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        conn.close()
        return True, "Database OK"
    except Exception as e:
        return False, f"Database error: {e}"

def check_ports():
    """Check required ports"""
    ports = [5000, 8080]
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result != 0:
            return False, f"Port {port} is not listening"
    return True, "All ports OK"

def check_system_resources():
    """Check system resources"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage('/').percent
    
    if cpu_percent > 90:
        return False, f"CPU usage too high: {cpu_percent}%"
    if memory_percent > 90:
        return False, f"Memory usage too high: {memory_percent}%"
    if disk_percent > 90:
        return False, f"Disk usage too high: {disk_percent}%"
    
    return True, f"Resources OK (CPU: {cpu_percent}%, MEM: {memory_percent}%, DISK: {disk_percent}%)"

def check_web_dashboard():
    """Check web dashboard accessibility"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            return True, "Web dashboard OK"
        return False, f"Web dashboard returned {response.status_code}"
    except Exception as e:
        return False, f"Web dashboard error: {e}"

def check_dependencies():
    """Check critical dependencies"""
    critical_imports = [
        'cryptography', 'paramiko', 'requests', 'psutil',
        'discord', 'telethon', 'slack_sdk'
    ]
    
    missing = []
    for module in critical_imports:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        return False, f"Missing dependencies: {', '.join(missing)}"
    return True, "All dependencies OK"

def main():
    """Main health check function"""
    checks = {
        'database': check_database(),
        'ports': check_ports(),
        'system': check_system_resources(),
        'web': check_web_dashboard(),
        'dependencies': check_dependencies()
    }
    
    all_passed = all(status for status, _ in checks.values())
    
    result = {
        'status': 'healthy' if all_passed else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {name: {'status': 'pass' if status else 'fail', 'message': msg} 
                   for name, (status, msg) in checks.items()}
    }
    
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()