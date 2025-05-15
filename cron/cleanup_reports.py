#!/usr/bin/env python3
import os
import sys

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import delete_old_reports

if __name__ == "__main__":
    """Script to delete reports older than the retention period
    
    This script can be run as a cron job:
    0 * * * * /path/to/cleanup_reports.py  # Run hourly
    """
    deleted_count = delete_old_reports()
    print(f"Deleted {deleted_count} reports older than 48 hours.")