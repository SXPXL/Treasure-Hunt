
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector

admin_level4_bp = Blueprint('admin_level4', __name__)

# Helper to get team clue order by score
def get_team_clue_order():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shantyjoshy@123",
        database="hunt"
    )
    cursor = con.cursor(dictionary=True)
    # Get all teams in users table (zero-padded)
    cursor.execute("SELECT team_num, score FROM users WHERE team_num != '00' ORDER BY score DESC, team_num ASC")
    user_teams = [row['team_num'] for row in cursor.fetchall()]
    # Get all teams in hunt table (as int)
    cursor.execute("SELECT team FROM hunt")
    hunt_teams = set(str(row['team']).zfill(2) for row in cursor.fetchall())
    # Only keep teams that exist in both
    teams = [t for t in user_teams if t in hunt_teams]
    cursor.close()
    con.close()
    return teams

# Helper to get clues/codes for a team
def get_team_clues(team_num):
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shantyjoshy@123",
        database="hunt"
    )
    cursor = con.cursor(dictionary=True)
    # Accept both zero-padded and non-padded team numbers
    try:
        team_int = int(team_num.lstrip('0')) if isinstance(team_num, str) else int(team_num)
    except Exception:
        team_int = int(team_num)
    cursor.execute("SELECT * FROM hunt WHERE team = %s", (team_int,))
    row = cursor.fetchone()
    cursor.close()
    con.close()
    return row

# Route to serve clues for hunt.html
@admin_level4_bp.route('/hunt', methods=['GET', 'POST'])
def hunt_clue():
    if 'team_num' not in session:
        return redirect(url_for('login'))
    team_num = session['team_num']
    # Get team order by score
    team_order = get_team_clue_order()
    if not team_order:
        return render_template('hunt.html', clue_text="No clues set for any team yet.", clue_num=1)
    # If the logged-in team is not in the clue order, assign them to the first team in the order
    if team_num not in team_order:
        team_index = 0
    else:
        team_index = team_order.index(team_num)
    # Each team gets clues from the next team in order (wrap around)
    clue_team_num = team_order[(team_index + 1) % len(team_order)]
    clues_row = get_team_clues(clue_team_num)
    if not clues_row:
        return render_template('hunt.html', clue_text="No clues set for your team yet.", clue_num=1)

    # Track progress in session (or DB for persistence)
    if 'hunt_clue_num' not in session:
        session['hunt_clue_num'] = 1
    clue_num = session['hunt_clue_num']

    # On POST, check code and advance
    if request.method == 'POST':
        code_input = request.form.get('number_input', '').strip()
        code_key = f'code{clue_num}'
        if code_input and clues_row.get(code_key) and code_input == str(clues_row[code_key]):
            clue_num += 1
            session['hunt_clue_num'] = clue_num
        else:
            # Wrong code, show same clue with error
            return render_template('hunt.html', clue_text=clues_row.get(f'clue{clue_num}', 'No more clues.'), clue_num=clue_num, error="Incorrect code. Try again.")

    # Show next clue or finish
    if clue_num > 5:
        return render_template('hunt.html', clue_text="Congratulations! You have completed the hunt.", clue_num=clue_num)
    clue_text = clues_row.get(f'clue{clue_num}', 'No more clues.')
    return render_template('hunt.html', clue_text=clue_text, clue_num=clue_num)

@admin_level4_bp.route('/level4', methods=['GET', 'POST'])
def level4():
    if request.method == 'POST':
        team = request.form.get('team')
        if not team or not team.isdigit():
            flash('Please select a valid team before submitting.')
            return redirect(url_for('admin_level4.level4'))
        clues = []
        codes = []
        missing_clues = []
        for i in range(1, 6):
            clue = request.form.get(f'clue{i}')
            code = request.form.get(f'code{i}')
            if not clue:
                missing_clues.append(i)
            clues.append(clue)
            codes.append(code)
        if missing_clues:
            flash(f'Please fill in all clues. Missing: {", ".join(str(x) for x in missing_clues)}')
            return redirect(url_for('admin_level4.level4'))
        # Check if team already exists in hunt table
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Shantyjoshy@123",
            database="hunt"
        )
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT team FROM hunt WHERE team = %s", (int(team),))
        existing = cursor.fetchone()
        # If exists and not confirmed, show warning
        if existing and not request.form.get('confirm_overwrite'):
            cursor.close()
            con.close()
            return render_template('level4.html', confirm_team=team, clues=clues, codes=codes)
        # Otherwise, update/insert
        cursor.close()
        cursor = con.cursor()
        cursor.execute(
            "REPLACE INTO hunt (team, clue1, code1, clue2, code2, clue3, code3, clue4, code4, clue5, code5) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (int(team), clues[0], codes[0], clues[1], codes[1], clues[2], codes[2], clues[3], codes[3], clues[4], codes[4])
        )
        con.commit()
        cursor.close()
        con.close()
        flash('Clues and codes saved!')
        return redirect(url_for('admin_level4.level4'))
    # Fetch all teams' clues and codes for display
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shantyjoshy@123",
        database="hunt"
    )
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT team, clue1, code1, clue2, code2, clue3, code3, clue4, code4, clue5, code5 FROM hunt ORDER BY team")
    teams_data = cursor.fetchall()
    cursor.close()
    con.close()
    return render_template('level4.html', teams_data=teams_data)
