#!/usr/bin/env python3
"""
API Decorator Enforcement Script
=================================

Automatically scans all API endpoints in urls.py and verifies they have
@api_login_required decorator. Can be used as:
- Pre-commit hook
- CI/CD pipeline check
- Manual validation
- Automated fix tool

Usage:
    python tools/check_api_decorators.py              # Check only
    python tools/check_api_decorators.py --fix        # Auto-apply decorators
    python tools/check_api_decorators.py --strict     # Exit 1 if any missing

Created: January 4, 2026
"""

import os
import re
import sys
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict


class APIDecoratorChecker:
    """Scans API endpoints and verifies authentication decorators"""
    
    # Whitelist: Endpoints that use alternative authentication (OAuth, API tokens)
    WHITELIST_ALTERNATIVE_AUTH = {
        # External integration APIs use @require_api_scope (OAuth tokens)
        'api_get_token',           # OAuth token endpoint
        'api_list_staff',          # External API with token auth
        'api_get_staff',           # External API with token auth
        'api_list_shifts',         # External API with token auth
        'api_list_leave_requests', # External API with token auth
        'api_export_payroll',      # External API with token auth
        'api_create_webhook',      # External API with token auth
        'api_get_info',            # External API with token auth
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scheduling_dir = project_root / 'scheduling'
        self.urls_file = self.scheduling_dir / 'urls.py'
        self.view_files = list(self.scheduling_dir.glob('*.py'))
        
    def extract_api_endpoints_from_urls(self) -> List[Dict[str, str]]:
        """
        Parse urls.py and extract all API endpoint definitions.
        
        Returns:
            List of dicts with 'path', 'view_name', 'url_name'
        """
        endpoints = []
        
        with open(self.urls_file, 'r') as f:
            content = f.read()
        
        # Pattern: path('api/...', view_function, name='...')
        # Also handles: path('api/...', views.view_function, name='...')
        pattern = r"path\(['\"]api/([^'\"]+)['\"],\s*([a-zA-Z_.]+),\s*name=['\"]([^'\"]+)['\"]\)"
        
        matches = re.finditer(pattern, content)
        
        for match in matches:
            api_path = match.group(1)
            view_name = match.group(2)
            url_name = match.group(3)
            
            # Strip 'views.' prefix if present
            if view_name.startswith('views.'):
                view_name = view_name[6:]
            
            endpoints.append({
                'path': f'api/{api_path}',
                'view_name': view_name,
                'url_name': url_name
            })
        
        return endpoints
    
    def find_function_in_files(self, func_name: str) -> Tuple[Path, int, List[str]]:
        """
        Find function definition across all view files.
        
        Returns:
            (file_path, line_number, decorators_list)
        """
        for view_file in self.view_files:
            if not view_file.name.startswith('views') and view_file.name != 'ai_recommendations.py':
                continue
            
            try:
                with open(view_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    # Look for function definition
                    if re.match(rf'^def {func_name}\s*\(', line):
                        # Scan backwards to find decorators
                        decorators = []
                        j = i - 1
                        while j >= 0 and (lines[j].strip().startswith('@') or lines[j].strip() == ''):
                            if lines[j].strip().startswith('@'):
                                decorators.append(lines[j].strip())
                            j -= 1
                        
                        return (view_file, i + 1, decorators)  # Line numbers are 1-indexed
            except Exception as e:
                print(f"Warning: Could not read {view_file}: {e}")
                continue
        
        return (None, 0, [])
    
    def check_has_api_decorator(self, decorators: List[str]) -> bool:
        """Check if decorator list contains @api_login_required"""
        return any('@api_login_required' in dec for dec in decorators)
    
    def scan_all_endpoints(self) -> Dict[str, List[Dict]]:
        """
        Scan all API endpoints and categorize by status.
        
        Returns:
            {
                'secured': [...],     # Has @api_login_required
                'missing': [...],     # Missing decorator
                'not_found': [...],   # Function not found
                'whitelisted': [...]  # Uses alternative auth
            }
        """
        endpoints = self.extract_api_endpoints_from_urls()
        
        results = {
            'secured': [],
            'missing': [],
            'not_found': [],
            'whitelisted': []
        }
        
        print(f"\n🔍 Scanning {len(endpoints)} API endpoints...\n")
        
        for endpoint in endpoints:
            view_name = endpoint['view_name']
            file_path, line_num, decorators = self.find_function_in_files(view_name)
            
            endpoint['file'] = file_path.name if file_path else 'NOT_FOUND'
            endpoint['line'] = line_num
            endpoint['decorators'] = decorators
            
            # Check whitelist first
            if view_name in self.WHITELIST_ALTERNATIVE_AUTH:
                results['whitelisted'].append(endpoint)
            elif file_path is None:
                results['not_found'].append(endpoint)
            elif self.check_has_api_decorator(decorators):
                results['secured'].append(endpoint)
            else:
                results['missing'].append(endpoint)
        
        return results
    
    def print_report(self, results: Dict[str, List[Dict]]):
        """Print detailed scan report"""
        
        total = len(results['secured']) + len(results['missing']) + len(results['not_found']) + len(results.get('whitelisted', []))
        secured_count = len(results['secured'])
        missing_count = len(results['missing'])
        not_found_count = len(results['not_found'])
        whitelisted_count = len(results.get('whitelisted', []))
        
        print("=" * 80)
        print("API AUTHENTICATION DECORATOR SCAN REPORT")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   Total API endpoints: {total}")
        print(f"   ✅ Secured with @api_login_required: {secured_count} ({secured_count/total*100:.1f}%)")
        print(f"   🔐 Alternative auth (OAuth/tokens): {whitelisted_count} ({whitelisted_count/total*100:.1f}%)")
        print(f"   ⚠️  Missing decorator: {missing_count} ({missing_count/total*100:.1f}%)")
        print(f"   ❌ Function not found: {not_found_count}")
        
        if results['secured']:
            print(f"\n✅ SECURED ENDPOINTS ({len(results['secured'])}):")
            by_file = defaultdict(list)
            for ep in results['secured']:
                by_file[ep['file']].append(ep)
            
            for file, eps in sorted(by_file.items()):
                print(f"\n   {file}:")
                for ep in sorted(eps, key=lambda x: x['line']):
                    print(f"      ✓ {ep['view_name']:<40} (line {ep['line']})")
        
        if results.get('whitelisted'):
            print(f"\n🔐 WHITELISTED (Alternative Auth) ({len(results['whitelisted'])}):")
            by_file = defaultdict(list)
            for ep in results['whitelisted']:
                by_file[ep['file']].append(ep)
            
            for file, eps in sorted(by_file.items()):
                print(f"\n   {file}:")
                for ep in sorted(eps, key=lambda x: x['line']):
                    decorators_str = ', '.join(ep['decorators'][:2]) if ep['decorators'] else 'None'
                    print(f"      🔐 {ep['view_name']:<40} (line {ep['line']}) - {decorators_str}")
        
        if results['missing']:
            print(f"\n⚠️  MISSING DECORATOR ({len(results['missing'])}):")
            for ep in sorted(results['missing'], key=lambda x: (x['file'], x['line'])):
                print(f"   ❌ {ep['view_name']:<40} in {ep['file']}:{ep['line']}")
                print(f"      Current decorators: {', '.join(ep['decorators']) if ep['decorators'] else 'None'}")
                print(f"      URL: {ep['path']}")
        
        if results['not_found']:
            print(f"\n❌ FUNCTION NOT FOUND ({len(results['not_found'])}):")
            for ep in results['not_found']:
                print(f"   ⚠️  {ep['view_name']:<40} (referenced in urls.py)")
        
        print("\n" + "=" * 80)
        
        if missing_count > 0:
            print("\n⚠️  SECURITY WARNING: Found API endpoints without authentication!")
            print("   Run with --fix to automatically apply decorators")
            return False
        else:
            print("\n✅ All API endpoints are properly secured!")
            return True
    
    def auto_fix_missing_decorators(self, results: Dict[str, List[Dict]]):
        """Automatically add @api_login_required to missing endpoints"""
        
        if not results['missing']:
            print("\n✅ No missing decorators to fix!")
            return
        
        print(f"\n🔧 Auto-fixing {len(results['missing'])} endpoints...\n")
        
        # Group by file for efficient batch updates
        by_file = defaultdict(list)
        for ep in results['missing']:
            if ep['file'] != 'NOT_FOUND':
                by_file[ep['file']].append(ep)
        
        for filename, endpoints in by_file.items():
            file_path = self.scheduling_dir / filename
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Check if import exists
            has_import = any('from .decorators_api import api_login_required' in line for line in lines)
            
            # Add import if missing
            if not has_import:
                # Find first import block and add after it
                for i, line in enumerate(lines):
                    if line.startswith('from django.') or line.startswith('import '):
                        # Find end of import block
                        j = i
                        while j < len(lines) and (lines[j].startswith('from ') or lines[j].startswith('import ') or lines[j].strip() == ''):
                            j += 1
                        # Insert import
                        lines.insert(j, 'from .decorators_api import api_login_required\n')
                        print(f"   ✓ Added import to {filename}")
                        break
            
            # Add decorators (work backwards to preserve line numbers)
            for ep in sorted(endpoints, key=lambda x: x['line'], reverse=True):
                line_idx = ep['line'] - 1  # Convert to 0-indexed
                
                # Find the indentation of the function
                indent = len(lines[line_idx]) - len(lines[line_idx].lstrip())
                decorator_line = ' ' * indent + '@api_login_required\n'
                
                # Insert decorator before function
                lines.insert(line_idx, decorator_line)
                print(f"   ✓ Added @api_login_required to {ep['view_name']} (line {ep['line']})")
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"   ✅ Updated {filename}\n")
        
        print("🎉 Auto-fix complete!")


def main():
    """Main entry point"""
    
    # Detect project root (go up from tools/ to project root)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Parse arguments
    auto_fix = '--fix' in sys.argv
    strict = '--strict' in sys.argv
    
    print(f"Project root: {project_root}")
    print(f"Mode: {'Auto-fix' if auto_fix else 'Check only'}")
    
    checker = APIDecoratorChecker(project_root)
    results = checker.scan_all_endpoints()
    
    if auto_fix:
        checker.auto_fix_missing_decorators(results)
        # Re-scan after fix
        print("\n" + "=" * 80)
        print("RE-SCANNING AFTER AUTO-FIX...")
        print("=" * 80)
        results = checker.scan_all_endpoints()
    
    all_secure = checker.print_report(results)
    
    # Exit code
    if strict and not all_secure:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
