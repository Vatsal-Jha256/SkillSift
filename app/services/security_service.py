import os
import re
import json
import hashlib
import logging
import shutil
import datetime
import secrets
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.core.logging import logger
from app.core.config import settings
from app.services.audit_log_service import AuditLogService

class SecurityService:
    """Service for handling security and privacy-related operations."""
    
    @staticmethod
    def anonymize_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize personal information in the data.
        
        Args:
            data: Data containing personal information
            
        Returns:
            Anonymized data
        """
        if not data:
            return data
            
        # Create a deep copy to avoid modifying the original data
        anonymized = json.loads(json.dumps(data))
        
        # Anonymize contact information if present
        if "structured_data" in anonymized and anonymized["structured_data"]:
            if "contact_info" in anonymized["structured_data"] and anonymized["structured_data"]["contact_info"]:
                contact_info = anonymized["structured_data"]["contact_info"]
                
                # Anonymize email
                if "email" in contact_info and contact_info["email"]:
                    email = contact_info["email"]
                    username, domain = email.split('@')
                    anonymized["structured_data"]["contact_info"]["email"] = f"{username[:2]}{'*' * (len(username) - 2)}@{domain}"
                
                # Anonymize phone
                if "phone" in contact_info and contact_info["phone"]:
                    phone = contact_info["phone"]
                    anonymized["structured_data"]["contact_info"]["phone"] = f"{'*' * (len(phone) - 4)}{phone[-4:]}"
                
                # Anonymize address
                if "address" in contact_info and contact_info["address"]:
                    anonymized["structured_data"]["contact_info"]["address"] = "*** Address Hidden ***"
        
        return anonymized
    
    @staticmethod
    def secure_file_handling(file_content: bytes, original_filename: str, allowed_extensions: List[str] = None) -> tuple:
        """
        Handle files securely by validating extensions and generating a secure filename.
        
        Args:
            file_content: Content of the file
            original_filename: Original filename
            allowed_extensions: List of allowed file extensions (default: ['.pdf', '.docx', '.txt'])
            
        Returns:
            tuple: (secure_filename, file_path)
        """
        if allowed_extensions is None:
            allowed_extensions = ['.pdf', '.docx', '.txt']
            
        # Extract file extension
        _, extension = os.path.splitext(original_filename)
        
        # Validate file extension
        if extension.lower() not in allowed_extensions:
            raise ValueError(f"File extension not allowed. Allowed extensions: {', '.join(allowed_extensions)}")
        
        # Generate a random token to prevent filename guessing
        random_token = secrets.token_hex(8)
        
        # Generate a hash from the file content
        file_hash = hashlib.sha256(file_content).hexdigest()[:16]
        
        # Create a secure filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        secure_filename = f"{timestamp}_{random_token}_{file_hash}{extension.lower()}"
        
        # Define a secure file path using app settings
        # Use a more secure location than /tmp
        upload_dir = Path(getattr(settings, "SECURE_UPLOADS_DIR", "data/secure_uploads"))
        upload_dir.mkdir(exist_ok=True, parents=True)
        
        # Add user-specific subfolder for better isolation (if user_id is provided)
        file_path = upload_dir / secure_filename
        
        # Check against path traversal attacks
        if not os.path.normpath(str(file_path)).startswith(str(upload_dir)):
            raise ValueError("Invalid file path detected")
        
        # Set secure permissions
        os.umask(0o077)  # Ensures new files are created with 0600 permissions
        
        # Save the file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Verify file size matches expected size
        if os.path.getsize(file_path) != len(file_content):
            os.remove(file_path)
            raise ValueError("File integrity check failed")
        
        return secure_filename, file_path
    
    @staticmethod
    def get_data_retention_policy() -> Dict[str, Any]:
        """
        Get the data retention policy.
        
        Returns:
            Data retention policy
        """
        return {
            "resume_data": {
                "retention_period": "30 days",
                "reason": "Needed for analysis and report generation",
                "deletion_method": "Secure deletion"
            },
            "user_data": {
                "retention_period": "1 year",
                "reason": "Account maintenance and improvement of service",
                "deletion_method": "Anonymization followed by secure deletion"
            },
            "analytics_data": {
                "retention_period": "2 years",
                "reason": "Service improvement and research",
                "deletion_method": "Aggregation and anonymization"
            }
        }
    
    @staticmethod
    def get_gdpr_compliance_info() -> Dict[str, Any]:
        """
        Get GDPR compliance information.
        
        Returns:
            GDPR compliance information
        """
        return {
            "data_controller": {
                "name": "SkillSift",
                "contact_email": "privacy@skillsift.example.com"
            },
            "data_processing_purposes": [
                "Resume analysis and skill extraction",
                "Job compatibility scoring",
                "Report generation",
                "Service improvement"
            ],
            "data_subject_rights": [
                "Right to access",
                "Right to rectification",
                "Right to erasure (right to be forgotten)",
                "Right to restrict processing",
                "Right to data portability",
                "Right to object to processing",
                "Rights related to automated decision making and profiling"
            ],
            "data_retention": "See data retention policy"
        }
    
    @staticmethod
    def log_access(user_id: str, action: str, resource: str, status: str, details: Optional[str] = None) -> None:
        """
        Log access to resources for audit purposes.
        
        Args:
            user_id: ID of the user performing the action
            action: Action performed (e.g., 'read', 'write', 'delete')
            resource: Resource being accessed
            status: Status of the action (e.g., 'success', 'failure')
            details: Additional details about the access
        """
        # First, log to the regular log file
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details,
            "ip_address": getattr(getattr(getattr(logger, 'extra', {}), 'request', {}), 'client', {}).get('host', 'unknown')
        }
        
        # Log to application logger
        logger.info(f"AUDIT: {json.dumps(log_entry)}")
        
        # Also log to the cryptographically signed audit log
        AuditLogService.log_security_event(
            user_id=str(user_id),
            action=action,
            resource=resource,
            status=status,
            details=details
        )
        
        # Optional: Keep the old log file approach as a backup
        # Get audit log directory from settings or use default
        audit_log_dir = Path(getattr(settings, "AUDIT_LOGS_DIR", "data/audit_logs"))
        audit_log_dir.mkdir(exist_ok=True, parents=True)
        
        # Set secure permissions for the directory
        try:
            os.chmod(audit_log_dir, 0o700)  # Only owner can read/write/execute
        except Exception as e:
            logger.warning(f"Could not set permissions on audit log directory: {str(e)}")
        
        # Create log file with date-based naming
        log_date = datetime.datetime.now().strftime("%Y-%m-%d")
        audit_log_file = audit_log_dir / f"audit_{log_date}.log"
        
        # Append to log file with secure permissions
        with open(audit_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Set secure permissions for the log file
        try:
            os.chmod(audit_log_file, 0o600)  # Only owner can read/write
        except Exception as e:
            logger.warning(f"Could not set permissions on audit log file: {str(e)}")
        
        # Implement log rotation if needed
        SecurityService._rotate_logs(audit_log_dir)
    
    @staticmethod
    def _rotate_logs(log_dir: Path, max_logs: int = 30) -> None:
        """
        Rotate log files to prevent excessive disk usage.
        
        Args:
            log_dir: Directory containing log files
            max_logs: Maximum number of log files to keep
        """
        if not log_dir.exists():
            return
            
        log_files = sorted(list(log_dir.glob("audit_*.log")))
        
        # If we have more logs than the maximum, delete the oldest ones
        if len(log_files) > max_logs:
            for log_file in log_files[:-max_logs]:
                try:
                    os.remove(log_file)
                    logger.info(f"Rotated log file: {log_file.name}")
                except Exception as e:
                    logger.error(f"Error rotating log file {log_file}: {str(e)}")
    
    @staticmethod
    def securely_delete_file(file_path: Path) -> bool:
        """
        Securely delete a file by overwriting it multiple times before removal.
        
        Args:
            file_path: Path to the file to be deleted
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not file_path.exists():
            return True
            
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'wb') as f:
                # Multiple overwrite passes with different patterns
                for pattern in [b'\x00', b'\xFF', os.urandom(file_size)]:
                    f.seek(0)
                    if isinstance(pattern, bytes) and len(pattern) == 1:
                        f.write(pattern * file_size)
                    else:
                        f.write(pattern)
            
            # Finally delete the file
            os.remove(file_path)
            logger.info(f"Securely deleted file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error securely deleting file {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def securely_delete_directory(dir_path: Path) -> bool:
        """
        Securely delete all files in a directory and the directory itself.
        
        Args:
            dir_path: Path to the directory to be deleted
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not dir_path.exists():
            return True
            
        try:
            # Delete all files in the directory securely
            for file_path in dir_path.glob("**/*"):
                if file_path.is_file():
                    SecurityService.securely_delete_file(file_path)
            
            # Remove the empty directory
            shutil.rmtree(dir_path, ignore_errors=True)
            logger.info(f"Securely deleted directory: {dir_path}")
            return True
        except Exception as e:
            logger.error(f"Error securely deleting directory {dir_path}: {str(e)}")
            return False
    
    @staticmethod
    def encrypt_data(data: Dict[str, Any], user_id: str) -> str:
        """
        Simple encryption of data for secure storage.
        In a production environment, this should use proper encryption libraries
        
        Args:
            data: Data to encrypt
            user_id: User ID to associate with the data
            
        Returns:
            str: Encrypted data as a hex string
        """
        # In a real application, use a proper encryption library like cryptography
        # This is a simple placeholder implementation
        json_data = json.dumps(data)
        key = hashlib.sha256(f"{user_id}:{settings.SECRET_KEY}".encode()).digest()
        
        # Simple XOR operation (NOT secure for production)
        # In production, use proper authenticated encryption
        encrypted = []
        for i, char in enumerate(json_data.encode()):
            encrypted.append(char ^ key[i % len(key)])
        
        return bytes(encrypted).hex()
    
    @staticmethod
    def decrypt_data(encrypted_data: str, user_id: str) -> Dict[str, Any]:
        """
        Simple decryption of data.
        In a production environment, this should use proper encryption libraries
        
        Args:
            encrypted_data: Encrypted data as a hex string
            user_id: User ID associated with the data
            
        Returns:
            Dict: Decrypted data
        """
        # In a real application, use a proper encryption library like cryptography
        # This is a simple placeholder implementation
        key = hashlib.sha256(f"{user_id}:{settings.SECRET_KEY}".encode()).digest()
        
        # Convert hex to bytes
        encrypted_bytes = bytes.fromhex(encrypted_data)
        
        # Simple XOR operation (NOT secure for production)
        decrypted = []
        for i, char in enumerate(encrypted_bytes):
            decrypted.append(char ^ key[i % len(key)])
        
        return json.loads(bytes(decrypted).decode())
    
    @staticmethod
    def verify_export_access(export_id: str, user_id: str) -> bool:
        """
        Verify that a user has access to a specific data export.
        
        Args:
            export_id: Export ID to check
            user_id: User ID requesting access
            
        Returns:
            bool: True if access is allowed, False otherwise
        """
        exports_dir = Path(getattr(settings, "DATA_EXPORTS_DIR", "data/exports"))
        user_export_dir = exports_dir / f"user_{user_id}"
        
        # Check if the export directory exists and belongs to the user
        if not user_export_dir.exists():
            return False
            
        # Check for export_id directory
        export_dir = user_export_dir / export_id
        if export_dir.exists():
            return True
            
        # Check if the status file exists and matches the user
        for meta_file in user_export_dir.glob("*.json"):
            try:
                with open(meta_file, 'r') as f:
                    data = json.load(f)
                    if data.get("export_id") == export_id and str(data.get("user_id")) == str(user_id):
                        return True
            except Exception:
                pass
                
        return False
    
    @staticmethod
    def validate_export_id(export_id: str) -> bool:
        """
        Validate that an export ID has a proper format to prevent path traversal.
        
        Args:
            export_id: Export ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Export ID should only contain alphanumeric characters, dashes and underscores
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', export_id))
    
    @staticmethod
    def cleanup_expired_data(retention_days: int = 30, secure_delete: bool = True) -> None:
        """
        Clean up expired data based on the retention policy.
        
        Args:
            retention_days: Number of days to retain data
            secure_delete: Whether to perform secure deletion (overwrite before delete)
        """
        # Calculate the cutoff date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        
        # Clean up secure uploads
        upload_dir = Path(getattr(settings, "SECURE_UPLOADS_DIR", "data/secure_uploads"))
        if upload_dir.exists():
            for file_path in upload_dir.glob("*"):
                # Extract timestamp from filename
                try:
                    if file_path.is_file():
                        filename = file_path.name
                        # Extract date from filename (format: YYYYMMDD_HHMMSS_random_hash.ext)
                        date_str = filename.split("_")[0]
                        file_date = datetime.datetime.strptime(date_str, "%Y%m%d")
                        
                        if file_date < cutoff_date:
                            if secure_delete:
                                SecurityService.securely_delete_file(file_path)
                            else:
                                os.remove(file_path)
                            logger.info(f"Deleted expired file: {filename}")
                except Exception as e:
                    logger.error(f"Error cleaning up file {file_path}: {str(e)}")
        
        # Clean up expired data exports (older than retention period)
        exports_dir = Path(getattr(settings, "DATA_EXPORTS_DIR", "data/exports"))
        if exports_dir.exists():
            for export_dir in exports_dir.glob("*"):
                try:
                    if export_dir.is_dir():
                        # Check if the status file exists
                        status_file = export_dir / "status.json"
                        if status_file.exists():
                            with open(status_file, 'r') as f:
                                status_data = json.load(f)
                                completed_at = status_data.get("completed_at")
                                if completed_at:
                                    export_date = datetime.datetime.fromisoformat(completed_at)
                                    if export_date < cutoff_date:
                                        if secure_delete:
                                            SecurityService.securely_delete_directory(export_dir)
                                        else:
                                            shutil.rmtree(export_dir, ignore_errors=True)
                                        logger.info(f"Deleted expired data export: {export_dir.name}")
                except Exception as e:
                    logger.error(f"Error cleaning up export directory {export_dir}: {str(e)}")
        
        # Clean up audit logs based on retention policy
        audit_log_dir = Path(getattr(settings, "AUDIT_LOGS_DIR", "data/audit_logs"))
        if audit_log_dir.exists():
            for log_file in audit_log_dir.glob("audit_*.log"):
                try:
                    if log_file.is_file():
                        # Extract date from filename (format: audit_YYYY-MM-DD.log)
                        date_str = log_file.stem.split("_")[1]
                        log_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        
                        if log_date < cutoff_date:
                            # For secure logs, verify their integrity first
                            if "secure" in log_file.name:
                                # Verify log file before removing
                                result = AuditLogService.verify_log_chain(log_file)
                                
                                # Create a verification report
                                report_file = log_file.with_suffix(".verification")
                                with open(report_file, 'w') as f:
                                    json.dump(result, f, indent=2)
                                
                                # Only remove if verification was successful
                                if result.get("valid", False):
                                    os.remove(log_file)
                                    logger.info(f"Verified and rotated secure audit log: {log_file.name}")
                                else:
                                    logger.warning(f"Failed to verify secure audit log for rotation: {log_file.name}")
                            else:
                                # Regular logs can just be removed
                                os.remove(log_file)
                                logger.info(f"Rotated audit log: {log_file.name}")
                except Exception as e:
                    logger.error(f"Error cleaning up audit log {log_file}: {str(e)}") 