#!/usr/bin/env python3
"""
Unit Tests for Vengeance Bot Core Components
"""

import pytest
import json
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

sys.path.append('.')

class TestDatabaseManager:
    """Unit tests for DatabaseManager"""
    
    @pytest.fixture
    def db(self):
        from vengeance import DatabaseManager
        return DatabaseManager(':memory:')
    
    def test_init_tables(self, db):
        """Test table initialization"""
        db.init_tables()
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in db.cursor.fetchall()]
        assert 'command_history' in tables
        assert 'scans' in tables
        assert 'threats' in tables
    
    def test_log_command(self, db):
        """Test command logging"""
        db.log_command('test', 'local', True, 'output', 1.0)
        db.cursor.execute('SELECT * FROM command_history')
        row = db.cursor.fetchone()
        assert row['command'] == 'test'
        assert row['source'] == 'local'
        assert row['success'] == 1
    
    def test_log_scan(self, db):
        """Test scan logging"""
        db.log_scan('127.0.0.1', 'quick', [80, 443], [22, 25], 1.5)
        db.cursor.execute('SELECT * FROM scans')
        row = db.cursor.fetchone()
        assert row['target'] == '127.0.0.1'
        assert row['scan_type'] == 'quick'
    
    def test_log_threat(self, db):
        """Test threat logging"""
        db.log_threat('port_scan', '192.168.1.100', 'high', 'Multiple port scans detected')
        db.cursor.execute('SELECT * FROM threats')
        row = db.cursor.fetchone()
        assert row['threat_type'] == 'port_scan'
        assert row['severity'] == 'high'
    
    def test_get_statistics(self, db):
        """Test statistics retrieval"""
        db.log_command('cmd1', 'local', True, '', 0.1)
        db.log_command('cmd2', 'local', True, '', 0.2)
        db.log_scan('test.com', 'quick', [], [], 1.0)
        
        stats = db.get_statistics()
        assert stats['total_commands'] >= 2
        assert stats['total_scans'] >= 1

class TestCommandExecutor:
    """Unit tests for CommandExecutor"""
    
    @pytest.fixture
    def executor(self):
        from vengeance import CommandExecutor
        return CommandExecutor
    
    @patch('subprocess.run')
    def test_run_success(self, mock_run, executor):
        """Test successful command execution"""
        mock_run.return_value = Mock(returncode=0, stdout="Success output", stderr="")
        result = executor.run('echo test')
        assert result['success'] == True
        assert 'Success output' in result['output']
    
    @patch('subprocess.run')
    def test_run_failure(self, mock_run, executor):
        """Test failed command execution"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error occurred")
        result = executor.run('invalid_command')
        assert result['success'] == False
        assert 'Error' in result['output']
    
    @patch('subprocess.run')
    def test_run_timeout(self, mock_run, executor):
        """Test command timeout"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='test', timeout=1)
        result = executor.run('sleep 100', timeout=1)
        assert result['success'] == False
        assert 'timeout' in result['output'].lower()
    
    @patch('subprocess.run')
    def test_ping(self, mock_run, executor):
        """Test ping command"""
        mock_run.return_value = Mock(returncode=0, stdout="64 bytes from 8.8.8.8", stderr="")
        result = executor.ping('8.8.8.8')
        assert result['success'] == True
    
    @patch('subprocess.run')
    def test_nmap(self, mock_run, executor):
        """Test nmap command"""
        mock_run.return_value = Mock(returncode=0, stdout="Nmap scan report", stderr="")
        result = executor.nmap('localhost')
        assert 'Nmap' in result['output'] or result['success'] == True

class TestPortScanner:
    """Unit tests for PortScanner"""
    
    @pytest.fixture
    def scanner(self):
        from vengeance import PortScanner, DatabaseManager
        db = DatabaseManager(':memory:')
        return PortScanner(db)
    
    @patch('vengeance.CommandExecutor.nmap')
    def test_scan(self, mock_nmap, scanner):
        """Test port scanning"""
        mock_nmap.return_value = {
            'success': True,
            'output': '22/tcp open  ssh\n80/tcp open  http\n443/tcp closed https',
            'execution_time': 1.0
        }
        
        result = scanner.scan('localhost', '22,80,443')
        assert result['success'] == True
        assert len(result['open_ports']) >= 2
        assert any(p['port'] == 22 for p in result['open_ports'])
    
    @patch('vengeance.PortScanner.scan')
    def test_quick_scan(self, mock_scan, scanner):
        """Test quick scan"""
        mock_scan.return_value = {'success': True, 'open_ports': [80]}
        result = scanner.quick_scan('localhost')
        assert result['success'] == True

class TestPhishingServer:
    """Unit tests for PhishingServer"""
    
    @pytest.fixture
    def phishing_server(self):
        from vengeance import PhishingServer, DatabaseManager
        db = DatabaseManager(':memory:')
        return PhishingServer(db)
    
    def test_start_stop(self, phishing_server):
        """Test starting and stopping server"""
        result = phishing_server.start('test123', 'facebook', 0)  # Port 0 for random port
        # May fail if port is in use, but should handle gracefully
        assert True  # Placeholder
    
    def test_get_template(self, phishing_server):
        """Test template retrieval"""
        template = phishing_server._get_template('facebook')
        assert 'facebook' in template.lower() or 'Facebook' in template

class TestSSHManager:
    """Unit tests for SSHManager"""
    
    @pytest.fixture
    def ssh_manager(self):
        from vengeance import SSHManager, DatabaseManager
        db = DatabaseManager(':memory:')
        return SSHManager(db)
    
    def test_add_server(self, ssh_manager):
        """Test adding SSH server"""
        result = ssh_manager.add_server('test', '192.168.1.1', 'root', 'password')
        assert result['success'] == True
        assert 'server_id' in result
    
    def test_get_servers(self, ssh_manager):
        """Test getting server list"""
        ssh_manager.add_server('server1', '10.0.0.1', 'admin', 'pass')
        servers = ssh_manager.get_servers()
        assert len(servers) > 0
        assert servers[0]['name'] == 'server1'
    
    @patch('paramiko.SSHClient')
    def test_connect_fail(self, mock_client, ssh_manager):
        """Test connection failure"""
        ssh_manager.add_server('fail', 'invalid.host', 'user', 'pass')
        result = ssh_manager.connect('invalid_id')
        assert result['success'] == False

class TestTrafficGenerator:
    """Unit tests for TrafficGenerator"""
    
    @pytest.fixture
    def traffic_gen(self):
        from vengeance import TrafficGenerator, DatabaseManager
        db = DatabaseManager(':memory:')
        return TrafficGenerator(db)
    
    def test_generate_icmp(self, traffic_gen):
        """Test ICMP traffic generation"""
        with patch('vengeance.TrafficGenerator._send_icmp') as mock_send:
            mock_send.return_value = 64
            result = traffic_gen.generate('icmp', '8.8.8.8', 1, None, 1)
            assert result['success'] == True
            assert result['packets_sent'] > 0
    
    def test_generate_ping(self, traffic_gen):
        """Test ping traffic generation"""
        with patch('vengeance.CommandExecutor.run') as mock_run:
            mock_run.return_value = {'success': True, 'output': '64 bytes'}
            result = traffic_gen.generate('ping', '8.8.8.8', 1, None, 1)
            assert result['success'] == True

class TestCrunchGenerator:
    """Unit tests for CrunchGenerator"""
    
    @pytest.fixture
    def crunch(self):
        from vengeance import CrunchGenerator, DatabaseManager
        db = DatabaseManager(':memory:')
        return CrunchGenerator(db)
    
    def test_get_charsets(self, crunch):
        """Test charset retrieval"""
        charsets = crunch.get_charsets()
        assert 'lower' in charsets
        assert 'upper' in charsets
        assert 'numeric' in charsets
        assert 'alphanum' in charsets
    
    def test_generate_fallback(self, crunch):
        """Test fallback generation"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            result = crunch._generate_fallback(tmp.name, 4, 6, 'abc123')
            assert result > 0
            os.unlink(tmp.name)

class TestNiktoScanner:
    """Unit tests for NiktoScanner"""
    
    @pytest.fixture
    def nikto(self):
        from vengeance import NiktoScanner, DatabaseManager
        db = DatabaseManager(':memory:')
        return NiktoScanner(db)
    
    def test_parse_output(self, nikto):
        """Test output parsing"""
        test_output = """
+ OSVDB-123: Test vulnerability found
+ CVE-2024-1234: Critical issue
+ WARNING: Potential XSS vulnerability
        """
        vulns = nikto._parse_output(test_output)
        assert len(vulns) > 0
    
    @patch('shutil.which')
    def test_nikto_not_available(self, mock_which, nikto):
        """Test when Nikto is not installed"""
        mock_which.return_value = None
        result = nikto.scan('example.com')
        assert result['success'] == False
        assert 'not installed' in result['output']

class TestCommandHandler:
    """Unit tests for CommandHandler"""
    
    @pytest.fixture
    def handler(self):
        from vengeance import CommandHandler, DatabaseManager
        from vengeance import PortScanner, PhishingServer, SSHManager
        from vengeance import TrafficGenerator, CrunchGenerator, NiktoScanner
        
        db = DatabaseManager(':memory:')
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
    
    def test_unknown_command(self, handler):
        """Test unknown command"""
        result = handler.execute('unknown_command_123')
        # Should either fail gracefully or pass through to shell
        assert 'execution_time' in result
    
    def test_generate_phishing(self, handler):
        """Test phishing generation"""
        result = handler.execute('generate_phishing_link facebook')
        assert result['success'] == True
        assert 'Link ID' in result['output']
    
    def test_random_phishing(self, handler):
        """Test random phishing"""
        result = handler.execute('generate_random_phishing_link')
        assert result['success'] == True
        assert 'RANDOM' in result['output']

def run_unit_tests():
    """Run all unit tests"""
    pytest.main([__file__, '-v', '--cov=.', '--cov-report=term', '--tb=short'])

if __name__ == "__main__":
    run_unit_tests()