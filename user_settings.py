import sqlite3

class UserSettings:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create a table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                          user_id INTEGER PRIMARY KEY,
                          clip_seconds INTEGER,
                          car_camera_height REAL,
                          focal_length REAL)''')
        
        # Commit changes and close the connection
        conn.commit()
        conn.close()

    def save_settings(self, user_id, clip_seconds, car_camera_height, focal_length):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert or replace user settings
        cursor.execute('''INSERT OR REPLACE INTO settings 
                          (user_id, clip_seconds, car_camera_height, focal_length)
                          VALUES (?, ?, ?, ?)''', 
                       (user_id, clip_seconds, car_camera_height, focal_length))
        
        # Commit changes and close the connection
        conn.commit()
        conn.close()

    def get_settings(self, user_id):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Retrieve user settings
        cursor.execute('''SELECT user_id, clip_seconds, car_camera_height, focal_length 
                          FROM settings WHERE user_id = ?''', (user_id,))
        
        settings = cursor.fetchone()
        
        # Close the connection
        conn.close()
        
        # Return settings as a dictionary
        if settings:
            return {
                'USER_ID': settings[0],
                'CLIP_SECONDS': settings[1],
                'CAR_CAMERA_HEIGHT': settings[2],
                'FOCAL_LENGTH': settings[3]
            }
        else:
            return None


if __name__ == '__main__':
    db_path = 'db/user_settings.db'
    user_settings = UserSettings(db_path)
    user_settings.save_settings(1, 10, 0.8, 700)
    settings = user_settings.get_settings(1)
    print(settings)