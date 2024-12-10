from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import sqlite3
from datetime import datetime
import os

class DriveImageUploader:
    def __init__(self, service_account_path='service-account.json'):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.service_account_path = service_account_path
        self.service = self.authenticate_google_drive()
        self.db_path = 'images.db'
        self.setup_database()

    def authenticate_google_drive(self):
        """Authenticate with Google Drive using service account."""
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_path, 
            scopes=self.SCOPES
        )
        return build('drive', 'v3', credentials=credentials)

    def setup_database(self):
        """Create SQLite database and table if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                drive_url TEXT NOT NULL,
                upload_date TEXT NOT NULL,
                folder_path TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def get_or_create_folder(self, folder_name, parent_id=None):
        """Get folder ID or create if it doesn't exist."""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(
            q=query, spaces='drive', fields='files(id)').execute()
        files = results.get('files', [])

        if files:
            return files[0]['id']
        else:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata, fields='id').execute()
            return folder['id']

    def upload_image(self, image_path):
        """Upload image to Google Drive and save to database."""
        try:
            # Create main folder
            vehicle_folder_id = self.get_or_create_folder('vehicle_detection')

            # Create date folder
            current_date = datetime.now().strftime("%d-%m-%Y")
            date_folder_id = self.get_or_create_folder(current_date, vehicle_folder_id)

            # Upload file
            file_name = os.path.basename(image_path)
            file_metadata = {
                'name': file_name,
                'parents': [date_folder_id]
            }

            media = MediaFileUpload(image_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO images (filename, drive_url, upload_date, folder_path)
                VALUES (?, ?, ?, ?)
            ''', (
                file_name,
                file['webViewLink'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"vehicle_detection/{current_date}"
            ))
            conn.commit()
            conn.close()

            return {
                'success': True,
                'url': file['webViewLink'],
                'file_id': file['id'],
                'folder_path': f"vehicle_detection/{current_date}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_image_urls(self):
        """Retrieve all image URLs from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT filename, drive_url, upload_date, folder_path FROM images')
        results = cursor.fetchall()
        conn.close()
        return results

if __name__ == '__main__':
    # Initialize the uploader
    uploader = DriveImageUploader('service-account.json')

    # Upload an image
    result = uploader.upload_image('trip_images/trip1.png')

    if result['success']:
        print(f"Image uploaded successfully!")
        print(f"URL: {result['url']}")
        print(f"Folder path: {result['folder_path']}")
    else:
        print(f"Upload failed: {result['error']}")