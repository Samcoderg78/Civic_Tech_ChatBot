import sqlite3
import json
import os
from datetime import datetime, timedelta
from config import DATABASE_PATH, REPORT_RETENTION_HOURS

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Initialize database tables"""
    conn = get_db_connection()
    
    # Read schema file
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    
    conn.commit()
    conn.close()

def save_report(report_text, image_paths, latitude, longitude):
    """Save anonymous crime report to database"""
    conn = get_db_connection()
    
    # Convert image paths to JSON string
    images_json = json.dumps(image_paths)
    
    cursor = conn.execute(
        'INSERT INTO reports (report_text, latitude, longitude, images) VALUES (?, ?, ?, ?)',
        (report_text, latitude, longitude, images_json)
    )
    
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return report_id

def delete_old_reports():
    """Delete reports older than the retention period"""
    conn = get_db_connection()
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(hours=REPORT_RETENTION_HOURS)
    cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # First get the reports to delete so we can clean up image files
    cursor = conn.execute('SELECT images FROM reports WHERE timestamp < ?', (cutoff_str,))
    reports = cursor.fetchall()
    
    # Delete image files
    for report in reports:
        if report['images']:
            image_paths = json.loads(report['images'])
            for path in image_paths:
                if os.path.exists(path):
                    os.remove(path)
    
    # Now delete the records
    cursor = conn.execute('DELETE FROM reports WHERE timestamp < ?', (cutoff_str,))
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return deleted_count

def log_bait_car_notification(latitude, longitude):
    """Log when a bait car notification is sent"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO bait_car_logs (latitude, longitude, notification_sent) VALUES (?, ?, ?)',
        (latitude, longitude, True)
    )
    conn.commit()
    conn.close()