import mysql.connector

def sync_team_positions():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shantyjoshy@123",
        database="hunt"
    )
    cursor = con.cursor()
    # Get all team numbers from users (excluding admin)
    cursor.execute("SELECT team_num FROM users WHERE team_num != '00'")
    teams = [row[0] for row in cursor.fetchall()]
    for team_num in teams:
        cursor.execute("SELECT team_num FROM team_positions WHERE team_num = %s", (team_num,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO team_positions (team_num, score) VALUES (%s, 0)", (team_num,))
    con.commit()
    cursor.close()
    con.close()
    print('All teams synced to team_positions with score 0.')

if __name__ == '__main__':
    sync_team_positions()
