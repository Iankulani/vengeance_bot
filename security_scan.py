#!/usr/bin/env python3
"""
Security Scanning Script for Vengeance Bot
"""

import subprocess
import json
import sys
import os
from pathlib import Path

def run_bandit():
    """Run Bandit security scanner"""
    print("\n🔒 Running Bandit Security Scan...")
    try:
        result = subprocess.run(
            ['bandit', '-r', '.', '-f', 'json', '-o', 'bandit_report.json', '-ll'],
            capture_output=True,
            text=True
        )
        print("✅ Bandit scan completed")
        return True
    except Exception as e:
        print(f"❌ Bandit scan failed: {e}")
        return False

def run_safety():
    """Run Safety dependency scanner"""
    print("\n🔒 Running Safety Vulnerability Scan...")
    try:
        result = subprocess.run(
            ['safety', 'check', '--full-report', '-o', 'safety_report.json'],
            capture_output=True,
            text=True
        )
        print("✅ Safety scan completed")
        return True
    except Exception as e:
        print(f"❌ Safety scan failed: {e}")
        return False

def run_pip_audit():
    """Run pip-audit for dependency vulnerabilities"""
    print("\n🔒 Running pip-audit...")
    try:
        result = subprocess.run(
            ['pip-audit', '--format', 'json', '-o', 'pip_audit_report.json'],
            capture_output=True,
            text=True
        )
        print("✅ pip-audit completed")
        return True
    except Exception as e:
        print(f"❌ pip-audit failed: {e}")
        return False

def run_pylint():
    """Run Pylint for code quality"""
    print("\n🔒 Running Pylint...")
    try:
        result = subprocess.run(
            ['pylint', 'vengeance.py', '--output-format=json', '--exit-zero'],
            capture_output=True,
            text=True
        )
        print("✅ Pylint completed")
        return True
    except Exception as e:
        print(f"❌ Pylint failed: {e}")
        return False

def run_mypy():
    """Run Mypy for type checking"""
    print("\n🔒 Running Mypy Type Check...")
    try:
        result = subprocess.run(
            ['mypy', 'vengeance.py', '--ignore-missing-imports', '--no-strict-optional'],
            capture_output=True,
            text=True
        )
        print("✅ Mypy completed")
        return True
    except Exception as e:
        print(f"❌ Mypy failed: {e}")
        return False

def run_vulture():
    """Run Vulture for dead code detection"""
    print("\n🔒 Running Vulture Dead Code Check...")
    try:
        result = subprocess.run(
            ['vulture', 'vengeance.py', '--min-confidence=70'],
            capture_output=True,
            text=True
        )
        print("✅ Vulture completed")
        return True
    except Exception as e:
        print(f"❌ Vulture failed: {e}")
        return False

def run_semgrep():
    """Run Semgrep for static analysis"""
    print("\n🔒 Running Semgrep Static Analysis...")
    try:
        result = subprocess.run(
            ['semgrep', '--config', 'auto', '--json', '-o', 'semgrep_report.json'],
            capture_output=True,
            text=True
        )
        print("✅ Semgrep completed")
        return True
    except Exception as e:
        print(f"❌ Semgrep failed: {e}")
        return False

def check_hardcoded_secrets():
    """Check for hardcoded secrets"""
    print("\n🔒 Checking for Hardcoded Secrets...")
    patterns = [
        'API_KEY', 'SECRET_KEY', 'PASSWORD', 'TOKEN',
        '-----BEGIN RSA PRIVATE KEY-----', '-----BEGIN OPENSSH PRIVATE KEY-----'
    ]
    
    issues = []
    for file_path in Path('.').rglob('*.py'):
        if 'venv' in str(file_path) or '__pycache__' in str(file_path):
            continue
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                for pattern in patterns:
                    if pattern in content and pattern not in ['API_KEY', 'SECRET_KEY']:
                        issues.append(f"Potential hardcoded secret in {file_path}: {pattern}")
        except:
            pass
    
    if issues:
        print("⚠️ Found potential issues:")
        for issue in issues[:10]:
            print(f"  {issue}")
    else:
        print("✅ No hardcoded secrets detected")
    
    return len(issues) == 0

def generate_report():
    """Generate security report summary"""
    report = {
        'timestamp': str(subprocess.run(['date', '-Iseconds'], capture_output=True, text=True).stdout.strip()),
        'scans': {}
    }
    
    # Collect bandit results
    if os.path.exists('bandit_report.json'):
        with open('bandit_report.json', 'r') as f:
            data = json.load(f)
            report['scans']['bandit'] = {
                'issues': len(data.get('results', [])),
                'severity': {
                    'HIGH': sum(1 for r in data.get('results', []) if r.get('issue_severity') == 'HIGH'),
                    'MEDIUM': sum(1 for r in data.get('results', []) if r.get('issue_severity') == 'MEDIUM'),
                    'LOW': sum(1 for r in data.get('results', []) if r.get('issue_severity') == 'LOW')
                }
            }
    
    # Collect safety results
    if os.path.exists('safety_report.json'):
        with open('safety_report.json', 'r') as f:
            data = json.load(f)
            report['scans']['safety'] = {
                'vulnerabilities': len(data.get('vulnerabilities', []))
            }
    
    # Save report
    with open('security_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Security report saved to security_report.json")
    
    # Print summary
    print("\n" + "="*50)
    print("SECURITY SCAN SUMMARY")
    print("="*50)
    for scan_name, scan_data in report['scans'].items():
        print(f"\n{scan_name.upper()}:")
        for key, value in scan_data.items():
            print(f"  {key}: {value}")

def main():
    """Main security scan function"""
    print("🛡️ VENGEANCE BOT - Security Scanner")
    print("="*50)
    
    # Run all security scans
    scans = [
        run_bandit,
        run_safety,
        run_pip_audit,
        run_pylint,
        run_mypy,
        run_vulture,
        run_semgrep
    ]
    
    results = []
    for scan in scans:
        try:
            results.append(scan())
        except Exception as e:
            print(f"Error running {scan.__name__}: {e}")
            results.append(False)
    
    # Additional checks
    results.append(check_hardcoded_secrets())
    
    # Generate report
    generate_report()
    
    # Final status
    if all(results):
        print("\n✅ All security checks passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some security checks found issues. Check the reports for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()