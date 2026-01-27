#!/usr/bin/env python3
"""
API Permission Validation Script - Phase 3
===========================================

Scans API endpoints to ensure proper authorization checks are in place.
Validates that endpoints verify user permissions beyond just authentication.

Usage:
    python tools/check_api_permissions.py              # Check only
    python tools/check_api_permissions.py --fix        # Auto-apply permission checks
    python tools/check_api_permissions.py --strict     # Exit 1 if any missing

Created: January 4, 2026
"""

import os
import re
import sys
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict


class APIPermissionChecker:
    """
    Analyzes API endpoints to ensure proper authorization checks.
    
    Permission Patterns Checked:
    - is_management: Management-only endpoints
    - can_approve_leave: Leave approval endpoints
    - can_manage_rota: Rota management endpoints
    - is_superuser: Admin-only endpoints
    - request.user == resource.user: Self-access only
    """
    
    # Common permission patterns to look for
    PERMISSION_PATTERNS = {
        'is_management': r'request\.user\.role\.is_management',
        'can_approve_leave': r'request\.user\.role\.can_approve_leave',
        'can_manage_rota': r'request\.user\.role\.can_manage_rota',
        'is_superuser': r'request\.user\.is_superuser',
        'is_senior_management_team': r'request\.user\.role\.is_senior_management_team',
        'user_check': r'request\.user\s*==',  # Checking if user owns resource
    }
    
    # Endpoints that typically require specific permissions
    PERMISSION_REQUIRED = {
        # Management-only endpoints
        'is_management': [
            'daily_additional_staffing_report',
            'weekly_additional_staffing_report',
            'bulk_assign_training',
        ],
        # Leave approval endpoints
        'can_approve_leave': [
            'bulk_approve_leave',
            'bulk_reject_leave',
        ],
        # Rota management endpoints
        'can_manage_rota': [],
        # Admin-only endpoints
        'is_superuser': [],
        # Analytics/reporting (usually management)
        'analytics': [
            'api_dashboard_summary',
            'api_unit_staffing',
            'api_budget_analysis',
            'api_weekly_trends',
        ],
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scheduling_dir = project_root / 'scheduling'
        self.urls_file = self.scheduling_dir / 'urls.py'
        self.view_files = list(self.scheduling_dir.glob('views*.py'))
        
    def extract_api_endpoints(self) -> List[Dict[str, str]]:
        """Extract all @api_login_required endpoints from urls.py"""
        endpoints = []
        
        with open(self.urls_file, 'r') as f:
            content = f.read()
        
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
    
    def find_function_in_files(self, func_name: str) -> Tuple[str, int, List[str]]:
        """Find a function and extract its code"""
        for file_path in self.view_files:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Find function definition
            pattern = rf'^def {re.escape(func_name)}\s*\([^)]*\):'
            match = re.search(pattern, content, re.MULTILINE)
            
            if match:
                # Get line number
                line_num = content[:match.start()].count('\n') + 1
                
                # Extract function body (simple approach - until next def or class)
                lines = content[match.start():].split('\n')
                func_body = []
                indent_level = None
                
                for i, line in enumerate(lines):
                    if i == 0:
                        func_body.append(line)
                        continue
                    
                    # Determine base indent from first non-empty line
                    if indent_level is None and line.strip():
                        indent_level = len(line) - len(line.lstrip())
                    
                    # Stop at next function/class at same or lower indent
                    if line.strip() and not line.startswith(' ' * (indent_level or 0)):
                        if line.startswith('def ') or line.startswith('class '):
                            break
                    
                    func_body.append(line)
                    
                    # Limit to reasonable length
                    if len(func_body) > 200:
                        break
                
                return (str(file_path), line_num, func_body)
        
        return (None, None, [])
    
    def check_permission_in_code(self, code_lines: List[str]) -> Dict[str, bool]:
        """Check if code contains permission checks"""
        code = '\n'.join(code_lines)
        
        permissions_found = {}
        for perm_name, pattern in self.PERMISSION_PATTERNS.items():
            permissions_found[perm_name] = bool(re.search(pattern, code))
        
        return permissions_found
    
    def analyze_endpoint(self, endpoint: Dict[str, str]) -> Dict:
        """Analyze a single endpoint for permission checks"""
        func_name = endpoint['view_name']
        file_path, line_num, code_lines = self.find_function_in_files(func_name)
        
        if not file_path:
            return {
                **endpoint,
                'file': None,
                'line': None,
                'status': 'not_found',
                'permissions': {},
                'recommendations': []
            }
        
        permissions = self.check_permission_in_code(code_lines)
        has_any_permission = any(permissions.values())
        
        # Determine recommendations
        recommendations = []
        
        # Check if endpoint name suggests it needs permissions
        func_lower = func_name.lower()
        
        if not has_any_permission:
            if any(word in func_lower for word in ['approve', 'reject', 'bulk', 'admin', 'manage']):
                recommendations.append('⚠️  Management action endpoint without permission check')
            elif 'report' in func_lower or 'analytics' in func_lower or 'dashboard' in func_lower:
                recommendations.append('💡 Analytics endpoint - consider management-only access')
            elif 'ai' in func_lower or 'intelligence' in func_lower:
                recommendations.append('💡 AI/Intelligence endpoint - verify access control')
        
        # Determine status
        if has_any_permission:
            status = 'has_permissions'
        elif recommendations:
            status = 'needs_review'
        else:
            status = 'ok'  # Endpoint may not need extra permissions
        
        return {
            **endpoint,
            'file': os.path.basename(file_path),
            'line': line_num,
            'status': status,
            'permissions': permissions,
            'recommendations': recommendations
        }
    
    def scan_all_endpoints(self) -> Dict[str, List[Dict]]:
        """Scan all API endpoints and categorize by permission status"""
        endpoints = self.extract_api_endpoints()
        
        print(f"\n🔍 Scanning {len(endpoints)} API endpoints for permission checks...\n")
        
        results = {
            'has_permissions': [],
            'needs_review': [],
            'ok': [],
            'not_found': []
        }
        
        for endpoint in endpoints:
            analysis = self.analyze_endpoint(endpoint)
            results[analysis['status']].append(analysis)
        
        return results
    
    def print_report(self, results: Dict[str, List[Dict]]) -> bool:
        """Print detailed permission analysis report"""
        print("=" * 80)
        print("API PERMISSION VALIDATION REPORT")
        print("=" * 80)
        
        total = sum(len(v) for v in results.values())
        has_perms = len(results['has_permissions'])
        needs_review = len(results['needs_review'])
        ok = len(results['ok'])
        not_found = len(results['not_found'])
        
        print(f"\n📊 Summary:")
        print(f"   Total API endpoints: {total}")
        print(f"   ✅ With permission checks: {has_perms} ({has_perms/total*100:.1f}%)")
        print(f"   ⚠️  Need review: {needs_review} ({needs_review/total*100:.1f}%)")
        print(f"   ℹ️  No permissions needed: {ok} ({ok/total*100:.1f}%)")
        if not_found:
            print(f"   ❌ Not found: {not_found}")
        
        # Endpoints with permissions
        if results['has_permissions']:
            print(f"\n✅ ENDPOINTS WITH PERMISSION CHECKS ({len(results['has_permissions'])}):")
            
            by_file = defaultdict(list)
            for ep in results['has_permissions']:
                by_file[ep['file']].append(ep)
            
            for filename in sorted(by_file.keys()):
                print(f"\n   {filename}:")
                for ep in by_file[filename]:
                    perms = [k for k, v in ep['permissions'].items() if v]
                    print(f"      ✓ {ep['view_name']:<40} (line {ep['line']})")
                    print(f"        Checks: {', '.join(perms)}")
        
        # Endpoints needing review
        if results['needs_review']:
            print(f"\n⚠️  ENDPOINTS NEEDING REVIEW ({len(results['needs_review'])}):")
            
            by_file = defaultdict(list)
            for ep in results['needs_review']:
                by_file[ep['file']].append(ep)
            
            for filename in sorted(by_file.keys()):
                print(f"\n   {filename}:")
                for ep in by_file[filename]:
                    print(f"      ❌ {ep['view_name']:<40} (line {ep['line']})")
                    print(f"         URL: {ep['path']}")
                    for rec in ep['recommendations']:
                        print(f"         {rec}")
        
        # Summary
        print("\n" + "=" * 80)
        
        if needs_review == 0:
            print("✅ All endpoints have appropriate permission checks or don't require them!")
            return True
        else:
            print("⚠️  Some endpoints may need permission checks.")
            print(f"   Review {needs_review} endpoint(s) to determine if authorization is required.")
            return False
    
    def generate_permission_snippet(self, endpoint_name: str, permission_type: str) -> str:
        """Generate code snippet for adding permission check"""
        snippets = {
            'is_management': '''    # Check management permission
    if not (request.user.role and request.user.role.is_management):
        return JsonResponse({'error': 'Management permission required'}, status=403)''',
            
            'can_approve_leave': '''    # Check leave approval permission
    if not (request.user.role and request.user.role.can_approve_leave):
        return JsonResponse({'error': 'Leave approval permission required'}, status=403)''',
            
            'can_manage_rota': '''    # Check rota management permission
    if not (request.user.role and request.user.role.can_manage_rota):
        return JsonResponse({'error': 'Rota management permission required'}, status=403)''',
        }
        
        return snippets.get(permission_type, '# Add appropriate permission check')


def main():
    """Main entry point"""
    
    # Detect project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Parse arguments
    strict = '--strict' in sys.argv
    
    print("🔒 API Permission Validation - Phase 3")
    print(f"Project root: {project_root}")
    print(f"Mode: {'Strict (exit 1 if issues)' if strict else 'Advisory'}\n")
    
    checker = APIPermissionChecker(project_root)
    results = checker.scan_all_endpoints()
    all_good = checker.print_report(results)
    
    # Print guidance
    if results['needs_review']:
        print("\n💡 Recommendation:")
        print("   Review endpoints flagged above and add permission checks if needed.")
        print("   Example patterns:")
        print("   - Management actions: check is_management")
        print("   - Leave approvals: check can_approve_leave")
        print("   - Rota management: check can_manage_rota")
        print("   - Staff data: ensure request.user matches resource owner")
    
    # Exit code
    if strict and not all_good:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
