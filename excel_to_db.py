import pandas as pd
import mysql.connector

# --- CONFIG ---
EXCEL_FILE = 'test_teams.xlsx'  # Change to your Excel file path
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shantyjoshy@123',
    'database': 'hunt',
}
TABLE = 'users'  # Change to your table name if needed

# --- READ EXCEL ---
df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
expected = ['team_num', 'password', 'participates', 'score', 'position', 'image_url']
if not all(col in df.columns for col in expected):
    raise Exception(f'Excel must contain columns: {expected}')
df['team_num'] = df['team_num'].astype(str).str.zfill(2)
rows = []
for _, r in df.iterrows():
    rows.append((
        r['team_num'],
        r['password'],
        r['participates'],
        int(r['score']) if pd.notna(r['score']) else 0,
        int(r['position']) if pd.notna(r['position']) else 0,
        r['image_url'] if pd.notna(r['image_url']) else ''
    ))
print('Rows to insert:', rows)

# --- DB INSERT ---
con = mysql.connector.connect(**DB_CONFIG)
con.autocommit = True
cursor = con.cursor()
sql = f'''
    INSERT INTO {TABLE} (team_num, password, participates, score, position, image_url)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        password=VALUES(password),
        participates=VALUES(participates),
        score=VALUES(score),
        position=VALUES(position),
        image_url=VALUES(image_url)
'''
cursor.executemany(sql, rows)
con.commit()
cursor.close()
con.close()
print(f'Inserted/updated {len(rows)} rows.')
