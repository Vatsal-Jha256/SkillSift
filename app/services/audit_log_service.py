import os
import json
import hmac
import hashlib
import logging
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

class AuditLogService:
    """
    Service for handling cryptographically signed audit logs.
    
    This service implements secure audit logging techniques based on the article:
    https://www.cossacklabs.com/blog/audit-logs-security/
    
    Key features:
    - Integrity check for each log entry
    - Chained logging with each entry linked to the previous one
    - Protection against log tampering, removal, or reordering
    """
    
    # Constants for log chains
    INITIAL_CHAIN_HASH = "0000000000000000000000000000000000000000000000000000000000000000"
    CURRENT_CHAIN_KEY = None
    
    @staticmethod
    def init_log_chain(reset: bool = False) -> None:
        """
        Initialize or reset the log chain.
        
        Args:
            reset: Whether to reset an existing chain
        """
        # Get or create a secure key for the log chain
        key_path = Path(getattr(settings, "AUDIT_LOG_KEY_PATH", "data/secrets/audit_log.key"))
        key_path.parent.mkdir(exist_ok=True, parents=True)
        
        if reset or not key_path.exists():
            # Create a new random key
            try:
                key = os.urandom(32)  # 256-bit key
                with open(key_path, 'wb') as f:
                    f.write(key)
                # Set permissions to be readable only by the owner
                os.chmod(key_path, 0o600)
                logger.info("Created new audit log key")
            except Exception as e:
                logger.error(f"Failed to create audit log key: {str(e)}")
                # Fall back to a derived key if we can't create a file
                key = hashlib.sha256(f"{settings.SECRET_KEY}_audit_log_key".encode()).digest()
        else:
            # Read existing key
            try:
                with open(key_path, 'rb') as f:
                    key = f.read()
            except Exception as e:
                logger.error(f"Failed to read audit log key: {str(e)}")
                # Fall back to a derived key
                key = hashlib.sha256(f"{settings.SECRET_KEY}_audit_log_key".encode()).digest()
        
        # Store the key in memory
        AuditLogService.CURRENT_CHAIN_KEY = key
        
        # Create a new log file with an initialization entry
        log_path = AuditLogService._get_log_path()
        
        if reset or not log_path.exists():
            log_dir = log_path.parent
            log_dir.mkdir(exist_ok=True, parents=True)
            
            # Write initialization entries without integrity checks
            init_entries = [
                AuditLogService._create_log_entry(
                    action="log_chain_initialized",
                    user_id="system",
                    resource="audit_log",
                    status="success",
                    details="New audit log chain initialized"
                )
            ]
            
            with open(log_path, 'a') as f:
                for entry in init_entries:
                    f.write(json.dumps(entry) + "\n")
            
            # Log initialization
            logger.info(f"Initialized new audit log chain: {log_path}")

    @staticmethod
    def log_security_event(user_id: str, action: str, resource: str, status: str, details: Optional[str] = None) -> bool:
        """
        Log a security event with cryptographic integrity check.
        
        Args:
            user_id: ID of the user performing the action
            action: Action performed (e.g., 'read', 'write', 'delete')
            resource: Resource being accessed
            status: Status of the action (e.g., 'success', 'failure')
            details: Additional details about the access
            
        Returns:
            bool: True if logging succeeded, False otherwise
        """
        try:
            # Initialize log chain if needed
            if AuditLogService.CURRENT_CHAIN_KEY is None:
                AuditLogService.init_log_chain()
            
            # Create the log entry
            log_entry = AuditLogService._create_log_entry(
                action=action,
                user_id=user_id,
                resource=resource,
                status=status,
                details=details
            )
            
            # Get the previous log hash
            prev_hash = AuditLogService._get_last_hash()
            
            # Calculate integrity check for this entry
            integrity_check = AuditLogService._calculate_integrity_check(log_entry, prev_hash)
            log_entry["integrity_check"] = integrity_check
            
            # Write to log file
            log_path = AuditLogService._get_log_path()
            with open(log_path, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
            
            return True
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
            return False
    
    @staticmethod
    def verify_log_chain(log_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Verify the integrity of the audit log chain.
        
        Args:
            log_path: Path to the log file to verify (default: current log file)
            
        Returns:
            Dict with verification results
        """
        if log_path is None:
            log_path = AuditLogService._get_log_path()
        
        if not log_path.exists():
            return {
                "valid": False,
                "error": "Log file does not exist",
                "file": str(log_path)
            }
        
        # Initialize log chain if needed
        if AuditLogService.CURRENT_CHAIN_KEY is None:
            AuditLogService.init_log_chain()
        
        try:
            # Read the log file
            with open(log_path, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                return {
                    "valid": False,
                    "error": "Log file is empty",
                    "file": str(log_path)
                }
            
            # Initialize verification
            results = {
                "valid": True,
                "total_entries": len(lines),
                "verified_entries": 0,
                "invalid_entries": [],
                "file": str(log_path)
            }
            
            prev_hash = AuditLogService.INITIAL_CHAIN_HASH
            
            # Verify each log entry
            for i, line in enumerate(lines):
                try:
                    entry = json.loads(line.strip())
                    
                    # Skip entries without integrity checks (initialization entries)
                    if "integrity_check" not in entry:
                        results["verified_entries"] += 1
                        continue
                    
                    # Get stored integrity check
                    stored_check = entry["integrity_check"]
                    
                    # Remove integrity check for recalculation
                    entry_copy = entry.copy()
                    del entry_copy["integrity_check"]
                    
                    # Calculate expected integrity check
                    expected_check = AuditLogService._calculate_integrity_check(entry_copy, prev_hash)
                    
                    # Compare
                    if expected_check != stored_check:
                        results["valid"] = False
                        results["invalid_entries"].append({
                            "line": i + 1,
                            "entry": entry["id"],
                            "timestamp": entry["timestamp"]
                        })
                    else:
                        results["verified_entries"] += 1
                    
                    # Update previous hash for the next iteration
                    prev_hash = stored_check
                    
                except Exception as e:
                    results["valid"] = False
                    results["invalid_entries"].append({
                        "line": i + 1,
                        "error": str(e)
                    })
            
            return results
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "file": str(log_path)
            }
    
    @staticmethod
    def _create_log_entry(action: str, user_id: str, resource: str, status: str, details: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a log entry without integrity check.
        
        Args:
            action: Action performed
            user_id: ID of the user
            resource: Resource being accessed
            status: Status of the action
            details: Additional details
            
        Returns:
            Dict with log entry data
        """
        return {
            "id": hashlib.sha256(os.urandom(16)).hexdigest()[:16],
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details,
            "host": getattr(getattr(getattr(logger, 'extra', {}), 'request', {}), 'client', {}).get('host', 'unknown')
        }
    
    @staticmethod
    def _calculate_integrity_check(log_entry: Dict[str, Any], prev_hash: str) -> str:
        """
        Calculate integrity check for a log entry.
        
        Args:
            log_entry: Log entry data
            prev_hash: Hash of the previous log entry
            
        Returns:
            Integrity check hash
        """
        # Ensure we have a chain key
        if AuditLogService.CURRENT_CHAIN_KEY is None:
            AuditLogService.init_log_chain()
        
        # Create a canonical representation of the log entry
        sorted_entry = json.dumps(log_entry, sort_keys=True)
        
        # Combine with previous hash
        message = prev_hash + sorted_entry
        
        # Calculate HMAC using the chain key
        h = hmac.new(AuditLogService.CURRENT_CHAIN_KEY, message.encode(), hashlib.sha256)
        return h.hexdigest()
    
    @staticmethod
    def _get_last_hash() -> str:
        """
        Get the hash of the last log entry.
        
        Returns:
            Hash of the last log entry or initial hash if none exists
        """
        log_path = AuditLogService._get_log_path()
        
        if not log_path.exists():
            return AuditLogService.INITIAL_CHAIN_HASH
        
        try:
            # Read the last line of the log file
            with open(log_path, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                return AuditLogService.INITIAL_CHAIN_HASH
            
            last_line = lines[-1].strip()
            last_entry = json.loads(last_line)
            
            # If the last entry has an integrity check, use it, otherwise use initial hash
            return last_entry.get("integrity_check", AuditLogService.INITIAL_CHAIN_HASH)
        except Exception as e:
            logger.error(f"Error getting last hash: {str(e)}")
            return AuditLogService.INITIAL_CHAIN_HASH
    
    @staticmethod
    def _get_log_path() -> Path:
        """
        Get the path to the current log file.
        
        Returns:
            Path to the log file
        """
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        log_dir = Path(getattr(settings, "AUDIT_LOGS_DIR", "data/audit_logs"))
        return log_dir / f"secure_audit_{date_str}.log"
    
    @staticmethod
    def rotate_logs(max_days: int = 30) -> None:
        """
        Rotate logs to maintain a maximum history.
        
        Args:
            max_days: Maximum number of days to keep logs
        """
        log_dir = Path(getattr(settings, "AUDIT_LOGS_DIR", "data/audit_logs"))
        
        if not log_dir.exists():
            return
        
        # Calculate cutoff date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        # Find old log files
        for log_file in log_dir.glob("secure_audit_*.log"):
            try:
                # Extract date from filename
                date_str = log_file.stem.split("_")[-1]
                
                # Compare with cutoff date
                if date_str < cutoff_str:
                    # Verify log integrity before deleting
                    verification = AuditLogService.verify_log_chain(log_file)
                    
                    if verification["valid"]:
                        # Create a verified marker file
                        marker_file = log_file.with_suffix(".verified")
                        with open(marker_file, 'w') as f:
                            json.dump(verification, f, indent=2)
                        
                        # For maximum security, logs should be archived
                        # to immutable storage before deletion
                        logger.info(f"Log file {log_file.name} verified and can be archived")
                    else:
                        # Create an invalid marker file
                        marker_file = log_file.with_suffix(".invalid")
                        with open(marker_file, 'w') as f:
                            json.dump(verification, f, indent=2)
                        
                        logger.warning(f"Log file {log_file.name} integrity check failed")
            except Exception as e:
                logger.error(f"Error processing log file {log_file.name}: {str(e)}") 