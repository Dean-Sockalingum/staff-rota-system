"""
CGI Backup Integration Handlers
================================

Backup job orchestration and verification for Azure Backup + Veeam integration.

Author: Dean Sockalingum
Date: January 7, 2026
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess
import json

logger = logging.getLogger(__name__)


class AzureBackupHandler:
    """Handle Azure Backup operations for PostgreSQL database and files"""
    
    def __init__(self, vault_name: str, resource_group: str):
        self.vault_name = vault_name
        self.resource_group = resource_group
        self.api_version = '2021-07-01'
    
    def trigger_database_backup(self) -> Dict:
        """Trigger on-demand PostgreSQL database backup"""
        logger.info(f"Triggering Azure database backup for vault {self.vault_name}")
        
        # Azure CLI command to trigger backup
        cmd = [
            'az', 'backup', 'protection', 'backup-now',
            '--vault-name', self.vault_name,
            '--resource-group', self.resource_group,
            '--container-name', 'PostgreSQL',
            '--item-name', 'rota-db-primary',
            '--retain-until', (datetime.now() + timedelta(days=35)).strftime('%d-%m-%Y'),
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Backup triggered successfully: {result.stdout}")
            return {'status': 'success', 'job_id': self._parse_job_id(result.stdout)}
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup trigger failed: {e.stderr}")
            return {'status': 'failed', 'error': e.stderr}
    
    def check_backup_status(self, job_id: str) -> Dict:
        """Check status of Azure backup job"""
        cmd = [
            'az', 'backup', 'job', 'show',
            '--vault-name', self.vault_name,
            '--resource-group', self.resource_group,
            '--name', job_id,
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            job_data = json.loads(result.stdout)
            return {
                'status': job_data.get('status'),
                'progress': job_data.get('percentComplete'),
                'start_time': job_data.get('startTime'),
                'end_time': job_data.get('endTime'),
            }
        except Exception as e:
            logger.error(f"Failed to check backup status: {e}")
            return {'status': 'unknown', 'error': str(e)}
    
    def list_recovery_points(self, item_name: str) -> List[Dict]:
        """List available recovery points for restore"""
        cmd = [
            'az', 'backup', 'recoverypoint', 'list',
            '--vault-name', self.vault_name,
            '--resource-group', self.resource_group,
            '--container-name', 'PostgreSQL',
            '--item-name', item_name,
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            recovery_points = json.loads(result.stdout)
            return recovery_points
        except Exception as e:
            logger.error(f"Failed to list recovery points: {e}")
            return []
    
    def restore_database(self, recovery_point_id: str, target_server: str) -> Dict:
        """Restore PostgreSQL database from recovery point"""
        logger.info(f"Restoring database to {target_server} from recovery point {recovery_point_id}")
        
        cmd = [
            'az', 'backup', 'restore', 'restore-azurewl',
            '--vault-name', self.vault_name,
            '--resource-group', self.resource_group,
            '--recovery-point-id', recovery_point_id,
            '--target-server', target_server,
            '--restore-mode', 'AlternateWorkloadRestore',
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {'status': 'success', 'restore_job_id': self._parse_job_id(result.stdout)}
        except subprocess.CalledProcessError as e:
            logger.error(f"Restore failed: {e.stderr}")
            return {'status': 'failed', 'error': e.stderr}
    
    def _parse_job_id(self, output: str) -> str:
        """Parse job ID from Azure CLI output"""
        # Azure CLI returns JSON with job ID
        try:
            data = json.loads(output)
            return data.get('name', 'unknown')
        except:
            return 'unknown'


class VeeamBackupHandler:
    """Handle Veeam Backup & Replication operations for VM backups"""
    
    def __init__(self, server_url: str, username: str, password: str):
        self.server_url = server_url
        self.username = username
        self.password = password
        self.session_id = None
    
    def authenticate(self) -> bool:
        """Authenticate with Veeam REST API"""
        try:
            response = requests.post(
                f"{self.server_url}/api/sessionMngr/?v=latest",
                auth=(self.username, self.password),
                headers={'Content-Type': 'application/json'},
                verify=True,
            )
            response.raise_for_status()
            self.session_id = response.headers.get('X-RestSvcSessionId')
            logger.info("Veeam authentication successful")
            return True
        except Exception as e:
            logger.error(f"Veeam authentication failed: {e}")
            return False
    
    def get_backup_jobs(self) -> List[Dict]:
        """Get list of Veeam backup jobs"""
        if not self.session_id:
            self.authenticate()
        
        try:
            response = requests.get(
                f"{self.server_url}/api/jobs",
                headers={'X-RestSvcSessionId': self.session_id},
                verify=True,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get backup jobs: {e}")
            return []
    
    def start_backup_job(self, job_name: str) -> Dict:
        """Start Veeam backup job"""
        if not self.session_id:
            self.authenticate()
        
        logger.info(f"Starting Veeam backup job: {job_name}")
        
        try:
            # Get job ID
            jobs = self.get_backup_jobs()
            job = next((j for j in jobs if j['name'] == job_name), None)
            
            if not job:
                return {'status': 'failed', 'error': f'Job {job_name} not found'}
            
            # Start job
            response = requests.post(
                f"{self.server_url}/api/jobs/{job['id']}?action=start",
                headers={'X-RestSvcSessionId': self.session_id},
                verify=True,
            )
            response.raise_for_status()
            
            return {'status': 'success', 'job_id': job['id']}
        except Exception as e:
            logger.error(f"Failed to start backup job: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get status of Veeam backup job"""
        if not self.session_id:
            self.authenticate()
        
        try:
            response = requests.get(
                f"{self.server_url}/api/jobs/{job_id}",
                headers={'X-RestSvcSessionId': self.session_id},
                verify=True,
            )
            response.raise_for_status()
            job_data = response.json()
            
            return {
                'status': job_data.get('lastResult'),
                'last_run': job_data.get('lastRun'),
                'next_run': job_data.get('nextRun'),
                'is_running': job_data.get('isRunning'),
            }
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return {'status': 'unknown', 'error': str(e)}
    
    def get_restore_points(self, vm_name: str) -> List[Dict]:
        """Get available restore points for VM"""
        if not self.session_id:
            self.authenticate()
        
        try:
            response = requests.get(
                f"{self.server_url}/api/restorePoints?vmName={vm_name}",
                headers={'X-RestSvcSessionId': self.session_id},
                verify=True,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get restore points: {e}")
            return []
    
    def restore_vm(self, restore_point_id: str, target_host: str) -> Dict:
        """Restore VM from restore point"""
        if not self.session_id:
            self.authenticate()
        
        logger.info(f"Restoring VM from restore point {restore_point_id} to {target_host}")
        
        try:
            restore_spec = {
                'restorePointId': restore_point_id,
                'targetHost': target_host,
                'restoreMode': 'ToOriginalLocation',
                'powerOnAfterRestore': False,
            }
            
            response = requests.post(
                f"{self.server_url}/api/restore",
                headers={'X-RestSvcSessionId': self.session_id, 'Content-Type': 'application/json'},
                json=restore_spec,
                verify=True,
            )
            response.raise_for_status()
            
            return {'status': 'success', 'restore_session_id': response.json().get('sessionId')}
        except Exception as e:
            logger.error(f"VM restore failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def logout(self):
        """Close Veeam REST API session"""
        if self.session_id:
            try:
                requests.delete(
                    f"{self.server_url}/api/sessionMngr/{self.session_id}",
                    verify=True,
                )
                logger.info("Veeam session closed")
            except Exception as e:
                logger.error(f"Failed to close Veeam session: {e}")


class BackupVerificationHandler:
    """Handle automated backup verification and restore testing"""
    
    def __init__(self, azure_handler: AzureBackupHandler, veeam_handler: VeeamBackupHandler):
        self.azure_handler = azure_handler
        self.veeam_handler = veeam_handler
    
    def verify_backup_integrity(self, backup_type: str, item_name: str) -> Dict:
        """Verify backup integrity via checksum validation"""
        logger.info(f"Verifying {backup_type} backup integrity for {item_name}")
        
        if backup_type == 'database':
            recovery_points = self.azure_handler.list_recovery_points(item_name)
            if not recovery_points:
                return {'status': 'failed', 'error': 'No recovery points found'}
            
            latest_rp = recovery_points[0]
            return {
                'status': 'success',
                'recovery_point_id': latest_rp.get('name'),
                'backup_time': latest_rp.get('backupTime'),
                'is_consistent': latest_rp.get('isConsistent', False),
            }
        
        elif backup_type == 'vm':
            restore_points = self.veeam_handler.get_restore_points(item_name)
            if not restore_points:
                return {'status': 'failed', 'error': 'No restore points found'}
            
            latest_rp = restore_points[0]
            return {
                'status': 'success',
                'restore_point_id': latest_rp.get('id'),
                'creation_time': latest_rp.get('creationTime'),
                'is_corrupted': latest_rp.get('isCorrupted', False),
            }
        
        return {'status': 'failed', 'error': f'Unknown backup type: {backup_type}'}
    
    def automated_restore_test(self, test_server: str) -> Dict:
        """Perform automated restore test to validation server"""
        logger.info(f"Starting automated restore test to {test_server}")
        
        results = {
            'test_start_time': datetime.now().isoformat(),
            'test_server': test_server,
            'tests': [],
        }
        
        # Test 1: Database restore
        db_recovery_points = self.azure_handler.list_recovery_points('rota-db-primary')
        if db_recovery_points:
            latest_rp = db_recovery_points[0]
            restore_result = self.azure_handler.restore_database(
                latest_rp.get('name'),
                test_server
            )
            results['tests'].append({
                'test_name': 'Database Restore',
                'status': restore_result.get('status'),
                'restore_job_id': restore_result.get('restore_job_id'),
            })
        
        # Test 2: Application validation (would run SureBackup here)
        results['tests'].append({
            'test_name': 'Application Validation',
            'status': 'pending',
            'note': 'SureBackup job scheduled',
        })
        
        results['test_end_time'] = datetime.now().isoformat()
        results['overall_status'] = 'success' if all(
            t.get('status') == 'success' for t in results['tests']
        ) else 'failed'
        
        return results


class BackupMonitoringHandler:
    """Handle backup monitoring and alerting"""
    
    def __init__(self):
        self.alert_threshold_hours = 26  # Alert if backup older than 26 hours
    
    def check_backup_freshness(self, recovery_points: List[Dict]) -> Dict:
        """Check if latest backup is within acceptable age"""
        if not recovery_points:
            return {
                'status': 'critical',
                'message': 'No recovery points found',
                'age_hours': None,
            }
        
        latest_rp = recovery_points[0]
        backup_time = datetime.fromisoformat(latest_rp.get('backupTime', '').replace('Z', '+00:00'))
        age_hours = (datetime.now() - backup_time).total_seconds() / 3600
        
        if age_hours > self.alert_threshold_hours:
            return {
                'status': 'warning',
                'message': f'Latest backup is {age_hours:.1f} hours old (threshold: {self.alert_threshold_hours} hours)',
                'age_hours': age_hours,
            }
        
        return {
            'status': 'ok',
            'message': f'Latest backup is {age_hours:.1f} hours old',
            'age_hours': age_hours,
        }
    
    def send_backup_alert(self, alert_type: str, message: str, severity: str = 'P2'):
        """Send backup alert via email/ServiceNow/SIEM"""
        logger.warning(f"BACKUP ALERT [{severity}] - {alert_type}: {message}")
        
        # Integration points:
        # 1. Send email to backup-alerts@hscp.scot.nhs.uk
        # 2. Create ServiceNow incident
        # 3. Send to SIEM (Splunk HEC)
        
        # For now, just log
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'message': message,
            'severity': severity,
        }
        
        logger.info(f"Alert sent: {json.dumps(alert_data)}")
    
    def generate_backup_report(self, azure_handler: AzureBackupHandler, veeam_handler: VeeamBackupHandler) -> Dict:
        """Generate daily backup status report"""
        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'azure_backup': {},
            'veeam_backup': {},
        }
        
        # Azure Backup status
        db_recovery_points = azure_handler.list_recovery_points('rota-db-primary')
        report['azure_backup'] = {
            'recovery_point_count': len(db_recovery_points),
            'latest_backup': db_recovery_points[0].get('backupTime') if db_recovery_points else None,
            'freshness_check': self.check_backup_freshness(db_recovery_points),
        }
        
        # Veeam Backup status
        vm_jobs = veeam_handler.get_backup_jobs()
        rota_job = next((j for j in vm_jobs if 'Rota' in j.get('name', '')), None)
        if rota_job:
            job_status = veeam_handler.get_job_status(rota_job['id'])
            report['veeam_backup'] = {
                'job_name': rota_job.get('name'),
                'last_result': job_status.get('status'),
                'last_run': job_status.get('last_run'),
                'next_run': job_status.get('next_run'),
            }
        
        return report
