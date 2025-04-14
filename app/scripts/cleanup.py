#!/usr/bin/env python
"""
Script to clean up expired data based on retention policy.
This script can be scheduled to run periodically (e.g., daily) using cron, systemd timers, or other scheduling systems.

Example cron entry to run daily at 2 AM:
0 2 * * * python /path/to/SkillSift/app/scripts/cleanup.py
"""

import os
import sys
import datetime
import argparse
import logging

# Add parent directory to sys.path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.services.security_service import SecurityService
from app.core.logging import logger

def parse_arguments():
    parser = argparse.ArgumentParser(description='Clean up expired data.')
    parser.add_argument(
        '--retention-days', 
        type=int, 
        default=30,
        help='Number of days to retain data (default: 30)'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Perform a dry run without actually deleting any data'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    logger.info("Starting data cleanup process")
    logger.info(f"Retention period: {args.retention_days} days")
    
    if args.dry_run:
        logger.info("DRY RUN: No files will be deleted")
    
    try:
        if args.dry_run:
            # Simulate cleanup without actually deleting anything
            logger.info("Simulating cleanup...")
            # Just log what would be deleted without actually deleting
            
            # Calculate the cutoff date
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=args.retention_days)
            
            # Check secure uploads
            from pathlib import Path
            upload_dir = Path("/tmp/secure_uploads")
            if upload_dir.exists():
                for file_path in upload_dir.glob("*"):
                    try:
                        if file_path.is_file():
                            filename = file_path.name
                            # Extract date from filename (format: YYYYMMDD_HHMMSS_hash.ext)
                            date_str = filename.split("_")[0]
                            file_date = datetime.datetime.strptime(date_str, "%Y%m%d")
                            
                            if file_date < cutoff_date:
                                logger.info(f"Would delete file: {filename}")
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {str(e)}")
            
            # Check audit logs
            audit_log_dir = Path("/tmp/audit_logs")
            if audit_log_dir.exists():
                for log_file in audit_log_dir.glob("audit_*.log"):
                    try:
                        if log_file.is_file():
                            # Extract date from filename (format: audit_YYYY-MM-DD.log)
                            date_str = log_file.stem.split("_")[1]
                            log_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                            
                            if log_date < cutoff_date:
                                logger.info(f"Would delete audit log: {log_file.name}")
                    except Exception as e:
                        logger.error(f"Error processing audit log {log_file}: {str(e)}")
        else:
            # Perform actual cleanup
            logger.info("Performing data cleanup...")
            SecurityService.cleanup_expired_data(retention_days=args.retention_days)
        
        logger.info("Cleanup process completed successfully")
        
    except Exception as e:
        logger.error(f"Error during cleanup process: {str(e)}")
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main() 