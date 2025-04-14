#!/usr/bin/env python3
"""
Audit Log Verification Utility

This script verifies the integrity of cryptographically signed audit logs.
It can be used to detect tampering, removal, or reordering of log entries.

Usage:
    python verify_audit_logs.py [options]

Options:
    --log-file PATH    Path to a specific log file to verify
    --log-dir PATH     Path to the log directory to verify all logs
    --days DAYS        Number of days of logs to verify (default: 7)
    --verbose, -v      Enable verbose output
    --json             Output results in JSON format
    --html             Generate an HTML report
    --help, -h         Show this help message and exit
"""

import os
import sys
import json
import logging
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the parent directory to the path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.audit_log_service import AuditLogService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Verify the integrity of audit logs')
    
    parser.add_argument('--log-file', type=str, help='Path to a specific log file to verify')
    parser.add_argument('--log-dir', type=str, help='Path to the log directory to verify all logs')
    parser.add_argument('--days', type=int, default=7, help='Number of days of logs to verify (default: 7)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--html', action='store_true', help='Generate an HTML report')
    
    return parser.parse_args()

def verify_log_file(log_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """Verify a single log file."""
    logger.info(f"Verifying log file: {log_path}")
    
    # Verify the log chain
    result = AuditLogService.verify_log_chain(log_path)
    
    # Print verbose details if requested
    if verbose and not result.get("valid", False):
        print(f"\nInvalid entries in {log_path.name}:")
        for entry in result.get("invalid_entries", []):
            print(f"  Line {entry.get('line')}: {entry.get('error') or 'Invalid integrity check'}")
            if 'timestamp' in entry:
                print(f"  Timestamp: {entry.get('timestamp')}")
            print("")
    
    return result

def verify_log_directory(log_dir: Path, days: int = 7, verbose: bool = False) -> List[Dict[str, Any]]:
    """Verify all log files in a directory."""
    logger.info(f"Verifying logs in directory: {log_dir}")
    
    # Calculate the cutoff date
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")
    
    results = []
    
    # Find log files
    for log_file in log_dir.glob("secure_audit_*.log"):
        try:
            # Extract date from filename
            date_str = log_file.stem.split("_")[-1]
            
            # Skip files older than the cutoff date
            if date_str < cutoff_str:
                logger.info(f"Skipping old log file: {log_file.name}")
                continue
            
            # Verify the log file
            result = verify_log_file(log_file, verbose)
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing log file {log_file.name}: {str(e)}")
            results.append({
                "valid": False,
                "error": str(e),
                "file": str(log_file)
            })
    
    return results

def generate_html_report(results: List[Dict[str, Any]], output_path: Optional[Path] = None) -> str:
    """Generate an HTML report from verification results."""
    if output_path is None:
        output_path = Path(f"audit_log_verification_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    
    # Count valid and invalid logs
    valid_count = sum(1 for r in results if r.get("valid", False))
    invalid_count = len(results) - valid_count
    
    # Create the HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Log Verification Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .summary {{ margin-bottom: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px; }}
        .valid {{ color: green; }}
        .invalid {{ color: red; }}
        .log-entry {{ margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .log-valid {{ background-color: #e6ffe6; }}
        .log-invalid {{ background-color: #ffe6e6; }}
        .invalid-entry {{ margin: 5px 0; padding: 5px; background-color: #fff0f0; border-left: 3px solid #ff0000; }}
        .details {{ margin-top: 5px; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>Audit Log Verification Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total logs verified: {len(results)}</p>
        <p class="valid">Valid logs: {valid_count}</p>
        <p class="invalid">Invalid logs: {invalid_count}</p>
    </div>
    
    <h2>Detailed Results</h2>
"""
    
    # Add detailed results for each log file
    for result in results:
        valid = result.get("valid", False)
        file_name = Path(result.get("file", "Unknown")).name
        
        html_content += f"""
    <div class="log-entry {'log-valid' if valid else 'log-invalid'}">
        <h3>{file_name} - <span class="{'valid' if valid else 'invalid'}">{valid}</span></h3>
        <p>Total entries: {result.get("total_entries", 0)}</p>
        <p>Verified entries: {result.get("verified_entries", 0)}</p>
"""
        
        if not valid:
            html_content += f"""
        <h4>Invalid Entries ({len(result.get("invalid_entries", []))})</h4>
"""
            
            for entry in result.get("invalid_entries", []):
                html_content += f"""
        <div class="invalid-entry">
            <p>Line: {entry.get('line', 'Unknown')}</p>
"""
                if 'error' in entry:
                    html_content += f"""
            <p>Error: {entry.get('error')}</p>
"""
                if 'timestamp' in entry:
                    html_content += f"""
            <p>Timestamp: {entry.get('timestamp')}</p>
"""
                html_content += """
        </div>
"""
        
        if "error" in result:
            html_content += f"""
        <p class="invalid">Error: {result.get("error")}</p>
"""
        
        html_content += """
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    # Write the HTML content to a file
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    logger.info(f"HTML report generated: {output_path}")
    return str(output_path)

def main():
    """Main function."""
    args = parse_arguments()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    results = []
    
    # Verify a single log file
    if args.log_file:
        log_path = Path(args.log_file)
        if not log_path.exists():
            logger.error(f"Log file does not exist: {log_path}")
            sys.exit(1)
        
        result = verify_log_file(log_path, args.verbose)
        results.append(result)
    
    # Verify all logs in a directory
    elif args.log_dir:
        log_dir = Path(args.log_dir)
        if not log_dir.exists():
            logger.error(f"Log directory does not exist: {log_dir}")
            sys.exit(1)
        
        results = verify_log_directory(log_dir, args.days, args.verbose)
    
    # Default behavior: verify logs in the default directory
    else:
        # Get the default log directory
        log_dir = Path(os.environ.get("AUDIT_LOGS_DIR", "data/audit_logs"))
        if not log_dir.exists():
            logger.error(f"Default log directory does not exist: {log_dir}")
            sys.exit(1)
        
        results = verify_log_directory(log_dir, args.days, args.verbose)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    
    # Generate HTML report
    if args.html:
        report_path = generate_html_report(results)
        print(f"HTML report generated: {report_path}")
    
    # Print summary if not in JSON mode
    if not args.json:
        valid_count = sum(1 for r in results if r.get("valid", False))
        invalid_count = len(results) - valid_count
        
        print("\nAudit Log Verification Summary:")
        print(f"Total logs verified: {len(results)}")
        print(f"Valid logs: {valid_count}")
        print(f"Invalid logs: {invalid_count}")
        
        # Print details of invalid logs
        if invalid_count > 0 and not args.verbose:
            print("\nInvalid logs:")
            for result in results:
                if not result.get("valid", False):
                    print(f"  {Path(result.get('file', 'Unknown')).name}: {result.get('error', 'Invalid integrity check')}")
    
    # Exit with error code if any log is invalid
    if any(not r.get("valid", False) for r in results):
        sys.exit(1)

if __name__ == "__main__":
    main() 