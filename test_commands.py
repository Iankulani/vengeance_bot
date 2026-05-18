#!/usr/bin/env python3
"""
Command Testing Suite for Vengeance Bot
"""

import pytest
import subprocess
import json
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# Import the bot components
sys.path.append('.')
from vengeance import CommandHandler, DatabaseManager, PortScanner

class TestCommands:
    """Test all command functionality"""
    
    @pytest.fixture
    def db(self):
        """Database fixture"""
        return DatabaseManager(':memory:')
    
    @pytest.fixture
    def handler(self, db):
        """Command handler fixture"""
        from vengeance import PortScanner, PhishingServer, SSHManager, TrafficGenerator, CrunchGenerator, NiktoScanner
        scanner = PortScanner(db)
        phishing = PhishingServer(db)
        ssh = SSHManager(db)
        traffic = TrafficGenerator(db)
        crunch = CrunchGenerator(db)
        nikto = NiktoScanner(db)
        return CommandHandler(db, scanner, phishing, ssh, traffic, crunch, nikto)
    
    def test_help_command(self, handler):
        """Test help command"""
        result = handler.execute('help')
        assert result['success'] == True
        assert 'HELP MENU' in result['output']
        assert 'scan' in result['output'].lower()
    
    def test_ping_command(self, handler):
        """Test ping command"""
        result = handler.execute('ping 127.0.0.1')
        assert result['success'] == True
        assert 'time' in result['output'].lower() or 'ttl' in result['output'].lower()
    
    def test_status_command(self, handler):
        """Test status command"""
        result = handler.execute('status')
        assert result['success'] == True
        assert 'VENGEANCE BOT' in result['output']
    
    def test_time_command(self, handler):
        """Test time command"""
        result = handler.execute('time')
        assert result['success'] == True
        assert ':' in result['output']
    
    def test_date_command(self, handler):
        """Test date command"""
        result = handler.execute('date')
        assert result['success'] == True
        assert len(result['output']) > 0
    
    def test_invalid_command(self, handler):
        """Test invalid command"""
        result = handler.execute('invalid_command_xyz123')
        assert result['success'] == False or 'not found' in result.get('output', '').lower()
    
    def test_phishing_generation(self, handler):
        """Test phishing link generation"""
        result = handler.execute('generate_phishing_link facebook')
        assert result['success'] == True
        assert 'Phishing link generated' in result['output']
    
    def test_random_phishing(self, handler):
        """Test random phishing generation"""
        result = handler.execute('generate_random_phishing_link')
        assert result['success'] == True
        assert 'RANDOM PHISHING LINK' in result['output']
    
    def test_crunch_charsets(self, handler):
        """Test crunch charsets command"""
        result = handler.execute('crunch_charsets')
        assert result['success'] == True
        assert 'Character Sets' in result['output']
    
    @patch('subprocess.run')
    def test_nmap_command(self, mock_run, handler):
        """Test nmap command with mock"""
        mock_run.return_value = Mock(returncode=0, stdout="Nmap scan report for localhost (127.0.0.1)", stderr="")
        result = handler.execute('nmap localhost')
        # Command should execute even with mock
        assert 'execution_time' in result
    
    def test_command_history(self, handler):
        """Test command history"""
        handler.execute('test1')
        handler.execute('test2')
        result = handler.execute('history 5')
        assert result['success'] == True
        assert 'test1' in result['output'] or 'test2' in result['output']
    
    def test_clear_command(self, handler):
        """Test clear command"""
        result = handler.execute('clear')
        assert result['success'] == True
    
    def test_empty_command(self, handler):
        """Test empty command"""
        result = handler.execute('')
        assert result['success'] == False
        assert 'Empty' in result['output']

class TestNetworkCommands:
    """Test network-related commands"""
    
    @pytest.fixture
    def handler(self):
        """Handler fixture with mocked network calls"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Mock output", stderr="")
            from vengeance import CommandHandler, DatabaseManager, PortScanner
            db = DatabaseManager(':memory:')
            scanner = PortScanner(db)
            handler = CommandHandler(db, scanner, None, None, None, None, None)
            yield handler
    
    def test_dns_command(self, handler):
        """Test DNS lookup command"""
        result = handler.execute('dns google.com')
        assert result['success'] == True or 'output' in result
    
    def test_whois_command(self, handler):
        """Test whois command"""
        result = handler.execute('whois google.com')
        assert 'execution_time' in result

class TestSSHCommands:
    """Test SSH-related commands"""
    
    @pytest.fixture
    def handler(self):
        """Handler fixture with SSH manager"""
        from vengeance import CommandHandler, DatabaseManager, PortScanner, SSHManager
        db = DatabaseManager(':memory:')
        scanner = PortScanner(db)
        ssh = SSHManager(db)
        handler = CommandHandler(db, scanner, None, ssh, None, None, None)
        return handler
    
    def test_ssh_add(self, handler):
        """Test adding SSH server"""
        result = handler.execute('ssh_add testserver 192.168.1.1 root password123')
        assert result['success'] == True
        assert 'added' in result['output'].lower()
    
    def test_ssh_list_empty(self, handler):
        """Test listing SSH servers when empty"""
        result = handler.execute('ssh_list')
        assert result['success'] == True
        assert 'No SSH servers' in result['output']
    
    def test_ssh_list_with_servers(self, handler):
        """Test listing SSH servers with data"""
        handler.execute('ssh_add server1 10.0.0.1 admin pass')
        result = handler.execute('ssh_list')
        assert result['success'] == True
        assert 'server1' in result['output']

class TestTrafficCommands:
    """Test traffic generation commands"""
    
    @pytest.fixture
    def handler(self):
        """Handler fixture with traffic generator"""
        from vengeance import CommandHandler, DatabaseManager, PortScanner, TrafficGenerator
        db = DatabaseManager(':memory:')
        scanner = PortScanner(db)
        traffic = TrafficGenerator(db)
        handler = CommandHandler(db, scanner, None, None, traffic, None, None)
        return handler
    
    def test_traffic_ping(self, handler):
        """Test ping traffic command"""
        with patch('vengeance.TrafficGenerator.generate') as mock_gen:
            mock_gen.return_value = {'packets_sent': 10, 'bytes_sent': 640}
            result = handler.execute('traffic_ping 8.8.8.8 2')
            assert result['success'] == True
            assert 'packets' in result['output']

class TestDatabaseCommands:
    """Test database operations"""
    
    def test_database_initialization(self):
        """Test database initialization"""
        db = DatabaseManager(':memory:')
        assert db.conn is not None
        db.init_tables()
        # Check if tables exist
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in db.cursor.fetchall()]
        assert 'command_history' in tables
        assert 'scans' in tables
        assert 'threats' in tables
    
    def test_log_command(self):
        """Test command logging"""
        db = DatabaseManager(':memory:')
        db.log_command('test command', 'local', True, 'output', 0.5)
        db.cursor.execute('SELECT * FROM command_history')
        result = db.cursor.fetchone()
        assert result is not None
        assert result['command'] == 'test command'
    
    def test_log_scan(self):
        """Test scan logging"""
        db = DatabaseManager(':memory:')
        db.log_scan('127.0.0.1', 'quick', [80, 443], [22, 25], 1.5)
        db.cursor.execute('SELECT * FROM scans')
        result = db.cursor.fetchone()
        assert result is not None
        assert result['target'] == '127.0.0.1'
    
    def test_get_statistics(self):
        """Test statistics retrieval"""
        db = DatabaseManager(':memory:')
        stats = db.get_statistics()
        assert 'total_commands' in stats
        assert 'total_scans' in stats

def run_command_tests():
    """Run all command tests with pytest"""
    pytest.main([__file__, '-v', '--tb=short', '--maxfail=5'])

if __name__ == "__main__":
    run_command_tests()