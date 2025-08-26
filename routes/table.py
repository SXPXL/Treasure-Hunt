from flask import Blueprint, render_template, request, redirect, url_for, flash
import mysql.connector

table_bp = Blueprint('table', __name__)

@table_bp.route('/table')
def table():
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
    return render_template('table.html', teams_data=teams_data)

@table_bp.route('/table/edit', methods=['POST'])
def table_edit():
    team = request.form.get('team')
    clues = [request.form.get(f'clue{i}') for i in range(1, 6)]
    codes = [request.form.get(f'code{i}') for i in range(1, 6)]
    # Optionally, validate clues/codes here
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shantyjoshy@123",
        database="hunt"
    )
    cursor = con.cursor()
    cursor.execute(
        "REPLACE INTO hunt (team, clue1, code1, clue2, code2, clue3, code3, clue4, code4, clue5, code5) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (int(team), clues[0], codes[0], clues[1], codes[1], clues[2], codes[2], clues[3], codes[3], clues[4], codes[4])
    )
    con.commit()
    cursor.close()
    con.close()
    flash('Team ' + str(team) + ' updated!')
    return redirect(url_for('table.table'))
