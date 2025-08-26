from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import mysql.connector

# Create a Blueprint for game constraints
game_constraints_bp = Blueprint('game_constraints', __name__)

@game_constraints_bp.route('/admin/game_constraints', methods=['GET', 'POST'])
def game_constraints():
    popup_data = None
    if request.method == 'POST':
        # Extract form data
        level = request.form.get('level')
        game_type = request.form.get('type')
        num_participants = request.form.get('num_participants')
        minutes = request.form.get('minutes')
        seconds = request.form.get('seconds')
        # Store/update the type for the selected level in the DB
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Shantyjoshy@123",
            database="hunt"
        )
        cursor = con.cursor()
        cursor.execute("REPLACE INTO level_types (level, type) VALUES (%s, %s)", (level, game_type))
        con.commit()
        cursor.close()
        con.close()
        # Prepare data for popup
        popup_data = {
            'level': level,
            'game_type': game_type,
            'num_participants': num_participants,
            'minutes': minutes,
            'seconds': seconds
        }
        return render_template('admin_game_constraints.html', popup_data=popup_data)
    return render_template('admin_game_constraints.html')
