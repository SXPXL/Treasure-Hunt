from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import os
from werkzeug.utils import secure_filename
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = 'your-very-secret-key-12345'  # Change this to a strong, random value in production

# Register admin_level4 blueprint
from routes.admin_level4 import admin_level4_bp
app.register_blueprint(admin_level4_bp)
# Register table blueprint
from routes.table import table_bp
app.register_blueprint(table_bp)


# Route for hunt page now handled in admin_level4 blueprint


# Endpoint to aggregate all level scores and update users table
@app.route('/aggregate_scores', methods=['POST'])
def aggregate_scores():
    try:
        cursor = con.cursor(dictionary=True)
        # Get all team numbers from users (excluding admin)
        cursor.execute("SELECT team_num FROM users WHERE team_num != '00'")
        teams = [row['team_num'] for row in cursor.fetchall()]
        cursor.close()
        for team_num in teams:
            total = 0
            # Sum all scores for this team from all level score tables
            for table in ['level1_scores', 'level2_scores', 'level3_scores', 'level4_scores']:
                try:
                    c2 = con.cursor(dictionary=True)
                    c2.execute(f"SELECT SUM(score) as total_score FROM {table} WHERE team_num = %s", (team_num,))
                    row = c2.fetchone()
                    c2.close()
                    if row and row.get('total_score') is not None:
                        total += int(row['total_score'])
                except Exception:
                    pass  # Table or column may not exist, skip
            c3 = con.cursor()
            c3.execute("UPDATE users SET score = %s WHERE team_num = %s", (total, team_num))
            c3.close()
        con.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def aggregate_scores_logic():
    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT team_num FROM users WHERE team_num != '00'")
        teams = [row['team_num'] for row in cursor.fetchall()]
        cursor.close()
        for team_num in teams:
            total = 0
            for table in ['level1_scores', 'level2_scores', 'level3_scores', 'level4_scores']:
                try:
                    c2 = con.cursor(dictionary=True)
                    # Only take the highest score for each team in each tabsle
                    c2.execute(f"SELECT MAX(score) as max_score FROM {table} WHERE team_num = %s", (team_num,))
                    row = c2.fetchone()
                    c2.close()
                    if row and row.get('max_score') is not None:
                        total += int(row['max_score'])
                except Exception:
                    pass
            c3 = con.cursor()
            c3.execute("UPDATE users SET score = %s WHERE team_num = %s", (total, team_num))
            c3.close()
        con.commit()
        return True
    except Exception as e:
        return False


# API endpoint to receive and store level 3 (task) score from frontend
@app.route('/submit-level3-score', methods=['POST'])
def submit_level3_score():
    data = request.get_json()
    team_num = data.get('team_num')
    score = data.get('score')
    if not team_num or score is None:
        return jsonify({'success': False, 'error': 'Missing team_num or score'}), 400
    try:
        cursor = con.cursor()
        # Insert or update the score for this team in level3_scores
        cursor.execute("""
            INSERT INTO level3_scores (team_num, score)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE score = VALUES(score)
        """, (team_num, score))
        con.commit()
        cursor.close()
        aggregate_scores_logic()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shantyjoshy@123",
    database="hunt"
)
con.autocommit = True

# API endpoint to receive and store level 2 scores from frontend
@app.route('/submit-level2-score', methods=['POST'])
def submit_level2_score():
    data = request.get_json()
    team_num = data.get('team_num')
    score = data.get('score')
    answers = data.get('answers')
    if not team_num or score is None:
        return jsonify({'success': False, 'error': 'Missing team_num or score'}), 400
    # Convert answers to the format '1:answer1,2:answer2,3:answer3'
    try:
        answer_strs = []
        if isinstance(answers, list):
            for idx, ans in enumerate(answers, 1):
                user_ans = ans.get('user', '')
                answer_strs.append(f"{idx}:{user_ans}")
        answers_db = ','.join(answer_strs)
        cursor = con.cursor()
        # Insert or update the score and answers for this team in level2_scores
        cursor.execute("""
            INSERT INTO level2_scores (team_num, score, answers)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE score = VALUES(score), answers = VALUES(answers)
        """, (team_num, score, answers_db))
        con.commit()
        cursor.close()
        aggregate_scores_logic()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- All route definitions follow below this line ---

# API endpoint to get scores for a level table
@app.route('/get_level_scores')
def get_level_scores():
    table = request.args.get('table')
    if table not in ['level1_scores', 'level2_scores', 'level3_scores', 'level4_scores']:
        return jsonify([])
    cursor = con.cursor(dictionary=True)
    cursor.execute(f"SELECT team_num FROM {table}")
    scores = cursor.fetchall()
    cursor.close()
    return jsonify(scores)

# API endpoint to update total scores in users table
@app.route('/update_team_scores', methods=['POST'])
def update_team_scores():
    data = request.get_json()
    cursor = con.cursor()
    for team_num, score in data.items():
        cursor.execute("UPDATE users SET score = %s WHERE team_num = %s", (score, team_num))
    con.commit()
    cursor.close()
    return jsonify({'success': True})

# Route for task game page
@app.route('/task')
def task():
    return render_template('task.html')

# Route for puzzle game page
@app.route('/puzzle')
def puzzle():
    return render_template('puzzle.html')

# Route for quiz game page
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')



con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shantyjoshy@123",
    database="hunt"
)
con.autocommit = True

# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Route for login page
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        team_num = request.form.get('team_num')
        password = request.form.get('password')
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE team_num = %s AND password = %s", (team_num, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['team_num'] = user['team_num']
            if user['team_num'] == '00':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid Team No or Password!')
            return render_template('login.html')
    return render_template('login.html')

# Route for home page

@app.route('/home')
def home():
    team_num = session.get('team_num')
    if not team_num:
        return redirect(url_for('login'))
    # Create a new connection for this request
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shantyjoshy@123",
        database="hunt"
    )
    cursor = con.cursor(dictionary=True)
    # Check if team is eliminated
    cursor.execute("SELECT reason FROM manual_elimination WHERE team_num = %s ORDER BY created_at DESC LIMIT 1", (team_num,))
    elim = cursor.fetchone()
    # Get current user's details
    cursor.execute("SELECT team_num FROM users WHERE team_num = %s", (team_num,))
    user = cursor.fetchone()
    # Get leaderboard (top 3 by score desc, then position asc)
    leaderboard = []  # No leaderboard since score/position columns are removed
    # Fetch level-type mapping from DB
    cursor.execute("SELECT level, type FROM level_types")
    level_types = {row['level']: row['type'] for row in cursor.fetchall()}

    # Check eliminated_round status for this team in team_positions
    cursor.execute("SELECT eliminated_round FROM team_positions WHERE team_num = %s", (team_num,))
    team_pos = cursor.fetchone()
    is_live_for_level4 = team_pos and team_pos.get('eliminated_round', '').strip().lower() == 'live'

    cursor.close()
    con.close()
    unlocked = session.get('unlocked', 1)  # Default to 1 if not set
    eliminated_message = None
    if elim:
        eliminated_message = f"Your team has been eliminated. Reason: {elim['reason']}"
    admin_quiz_level = session.get('admin_quiz_level')
    admin_quiz_direction = session.get('admin_quiz_direction')
    return render_template('home.html', unlocked=unlocked, user=user, leaderboard=leaderboard, eliminated_message=eliminated_message, admin_quiz_level=admin_quiz_level, admin_quiz_direction=admin_quiz_direction, level_types=level_types, is_live_for_level4=is_live_for_level4)



# Route for admin page
@app.route('/admin')
def admin():
    quiz_level = session.get('admin_quiz_level')
    quiz_direction = session.get('admin_quiz_direction')
    return render_template('admin.html', quiz_level=quiz_level, quiz_direction=quiz_direction)

# Route for admin profile page
@app.route('/admin/profile')
def admin_profile():
    return render_template('admin_profile.html')


# Admin feature: Team Details
@app.route('/admin/team_details')
def admin_team_details():
    # Fetch all teams and their members from the database
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT team_num, participates FROM users WHERE team_num != '00' ORDER BY team_num ASC")
    teams = cursor.fetchall()
    cursor.close()
    # Prepare data: split participates into list
    for team in teams:
        members = [m.strip() for m in (team['participates'] or '').split(',') if m.strip()]
        team['members'] = members
    return render_template('admin_team_details.html', teams=teams)

import pandas as pd
@app.route('/admin/upload_excel', methods=['POST'])
def admin_upload_excel():
    if 'excel_file' not in request.files:
        flash('No file part')
        return redirect(url_for('admin_team_details'))
    file = request.files['excel_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('admin_team_details'))
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        flash('Invalid file type!')
        return redirect(url_for('admin_team_details'))
    import os
    try:
        # Save uploaded file to disk
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        save_path = os.path.join(upload_folder, file.filename)
        file.save(save_path)
        flash(f'File saved to: {save_path}')
        print(f'File saved to: {save_path}')
        if not os.path.exists(save_path):
            flash('File not found after saving!')
            print('File not found after saving!')
            return redirect(url_for('admin_team_details'))
        # Now process the saved file using the same logic as excel_to_db.py
        import pandas as pd
        try:
            df = pd.read_excel(save_path, engine='openpyxl')
            print('DataFrame loaded:', df)
            flash(f'DataFrame loaded: {df.to_dict()}')
        except Exception as read_e:
            flash(f'Error reading Excel: {read_e}')
            print(f'Error reading Excel: {read_e}')
            return redirect(url_for('admin_team_details'))
        expected = ['team_num', 'password', 'participates', 'score', 'position', 'image_url']
        if not all(col in df.columns for col in expected):
            flash(f'Excel must contain columns: {expected}')
            print(f'Excel must contain columns: {expected}')
            return redirect(url_for('admin_team_details'))
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
        flash(f'Rows to insert: {rows}')
        cursor = con.cursor()
        sql = '''
            INSERT INTO users (team_num, password, participates, score, position, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                password=VALUES(password),
                participates=VALUES(participates),
                score=VALUES(score),
                position=VALUES(position),
                image_url=VALUES(image_url)
        '''
        try:
            cursor.executemany(sql, rows)
            con.commit()
            cursor.close()
            flash(f'Inserted/updated {len(rows)} rows.')
            print(f'Inserted/updated {len(rows)} rows.')
        except Exception as sql_e:
            flash(f'SQL error: {sql_e}')
            print(f'SQL error: {sql_e}')
        # Optionally, remove the uploaded file after processing
        try:
            os.remove(save_path)
        except Exception:
            pass
    except Exception as e:
        flash('Error processing file: ' + str(e))
        print('Error processing file:', e)
    return redirect(url_for('admin_team_details'))

# Route to remove a team from the database
@app.route('/admin/remove_team', methods=['POST'])
def admin_remove_team():
    team_num = request.form.get('team_num')
    if not team_num or team_num == '00':
        flash('Invalid team number!')
        return redirect(url_for('admin_team_details'))
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM users WHERE team_num = %s", (team_num,))
        con.commit()
        cursor.close()
        flash(f'Team {team_num} removed successfully!')
    except Exception as e:
        flash(f'Error removing team: {e}')
    return redirect(url_for('admin_team_details'))

# Admin feature: Leaderboard
@app.route('/admin/leaderboard')
def admin_leaderboard():
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT team_num, position FROM team_positions ORDER BY team_num ASC")
    positions = cursor.fetchall()
    cursor.close()
    return render_template('admin_leaderboard.html', positions=positions)

# Admin feature: Manual Elimination


# Admin feature: Game Constraints
from routes.game_constraints import game_constraints_bp
app.register_blueprint(game_constraints_bp)


# API endpoint to receive and store level 1 scores from frontend
@app.route('/submit-level1-score', methods=['POST'])
def submit_level1_score():
    data = request.get_json()
    team_num = data.get('team_num')
    score = data.get('score')
    if not team_num or score is None:
        return jsonify({'success': False, 'error': 'Missing team_num or score'}), 400
    try:
        cursor = con.cursor()
        cursor.execute("""
            INSERT INTO level1_scores (team_num, score)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE score = VALUES(score)
        """, (team_num, score))
        con.commit()
        cursor.close()
        aggregate_scores_logic()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Route for loading page
@app.route('/load')
def load():
    return render_template('load.html')



# Route for profile page
@app.route('/profile')
def profile():
    team_num = session.get('team_num')
    if not team_num:
        return redirect(url_for('login'))
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE team_num = %s", (team_num,))
    user = cursor.fetchone()
    cursor.close()
    if not user:
        flash('User not found!')
        return redirect(url_for('login'))
    # Split participants string into a list
    members = user['participates'].split(',') if user['participates'] else []
    profile_photo_url = user.get('image_url') if user.get('image_url') else None
    return render_template('profile.html', team_num=user['team_num'], members=members, profile_photo_url=profile_photo_url)

# Route to upload profile photo
@app.route('/upload_profile_photo', methods=['POST'])
def upload_profile_photo():
    if 'team_num' not in session:
        return redirect(url_for('login'))
    if 'profile_photo' not in request.files:
        flash('No file part')
        return redirect(url_for('profile'))
    file = request.files['profile_photo']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('profile'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        team_num = session['team_num']
        filename = f"profile_team{team_num}_" + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_url = f"/static/uploads/{filename}"
        cursor = con.cursor()
        cursor.execute("UPDATE users SET image_url = %s WHERE team_num = %s", (image_url, team_num))
        con.commit()
        cursor.close()
        flash('Profile photo updated!')
        return redirect(url_for('profile'))
    else:
        flash('Invalid file type!')
        return redirect(url_for('profile'))


@app.route('/gallery')
def gallery():
    team_num = session.get('team_num')
    if not team_num:
        return redirect(url_for('login'))
    cursor = con.cursor(dictionary=True)
    # Fetch all media URLs for this team from a new 'media' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INT AUTO_INCREMENT PRIMARY KEY,
            team_num VARCHAR(255),
            url VARCHAR(255),
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    cursor.execute("SELECT url FROM media WHERE team_num = %s ORDER BY uploaded_at DESC", (team_num,))
    media = [row['url'] for row in cursor.fetchall()]
    # Fetch profile photo URL and add to media if exists
    cursor.execute("SELECT image_url FROM users WHERE team_num = %s", (team_num,))
    user = cursor.fetchone()
    profile_photo_url = user['image_url'] if user and user.get('image_url') else None
    cursor.close()
    if profile_photo_url:
        # Insert at the beginning so profile photo is shown first
        media = [profile_photo_url] + media
    return render_template('gallery.html', images=media)


# Route for image upload from gallery
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'team_num' not in session:
        return redirect(url_for('login'))
    if 'image' not in request.files:
        flash('No file part')
        return redirect(url_for('gallery'))
    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('gallery'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        # Make filename unique per team and timestamp
        import time
        team_num = session['team_num']
        filename = f"team{team_num}_{int(time.time())}_" + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Save the URL to the new media table
        media_url = f"/static/uploads/{filename}"
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INT AUTO_INCREMENT PRIMARY KEY,
                team_num VARCHAR(255),
                url VARCHAR(255),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cursor.execute("INSERT INTO media (team_num, url) VALUES (%s, %s)", (team_num, media_url))
        con.commit()
        cursor.close()
        flash('Media uploaded successfully!')
        return redirect(url_for('gallery'))
    else:
        flash('Invalid file type!')
        return redirect(url_for('gallery'))

# Route for menu page
@app.route('/menu')
def menu():
    return render_template('menu.html')

# Route to delete media (must be after app and con are defined)
@app.route('/delete_media', methods=['POST'])
def delete_media():
    if 'team_num' not in session:
        return redirect(url_for('login'))
    team_num = session['team_num']
    media_url = request.form.get('media_url')
    if not media_url:
        flash('No media specified!')
        return redirect(url_for('gallery'))
    # Remove from DB
    cursor = con.cursor()
    cursor.execute("DELETE FROM media WHERE team_num = %s AND url = %s", (team_num, media_url))
    con.commit()
    cursor.close()
    # Remove file from disk
    try:
        file_path = media_url.lstrip('/')
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
    flash('Media deleted!')
    return redirect(url_for('gallery'))

import os
# Ensure manual_elimination table exists
def ensure_manual_elimination_table():
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manual_elimination (
            id INT AUTO_INCREMENT PRIMARY KEY,
            team_num VARCHAR(10) NOT NULL,
            reason TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    cursor.close()
ensure_manual_elimination_table()

@app.route('/admin/manual_elimination', methods=['GET', 'POST'])
def admin_manual_elimination():
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT team_num FROM users WHERE team_num != '00' ORDER BY team_num ASC")
    teams = cursor.fetchall()
    cursor.execute("SELECT team_num, reason, created_at FROM manual_elimination ORDER BY created_at DESC")
    eliminated_teams = cursor.fetchall()
    cursor.close()
    if request.method == 'POST':
        team_num = request.form.get('team_num')
        reason = request.form.get('reason')
        if not team_num or not reason:
            flash('Please select a team and enter a reason.')
        else:
            cursor = con.cursor()
            cursor.execute("INSERT INTO manual_elimination (team_num, reason) VALUES (%s, %s)", (team_num, reason))
            cursor.execute("UPDATE users SET active_or_not = 'not active' WHERE team_num = %s", (team_num,))
            con.commit()
            cursor.close()
            flash(f'Team {team_num} eliminated for: {reason}')
        return redirect(url_for('admin_manual_elimination'))
    return render_template('admin_manual_elimination.html', teams=teams, eliminated_teams=eliminated_teams)

@app.route('/level4')
def level4():
    return render_template('level4.html')

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)