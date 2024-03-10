from flask import Flask, render_template, request, make_response
import calendar
import datetime
import os
import logging

app = Flask(__name__)
logging.basicConfig(filename='app.log', level=logging.DEBUG)

def load_studied_days():
    """Load studied days from a file."""
    studied_days = set()
    file_path = os.path.join(os.getcwd(), 'studied_days.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:  # skip empty lines
                    try:
                        studied_day = datetime.datetime.strptime(line, "%Y-%m-%d").date()
                        studied_days.add(studied_day)
                    except ValueError:
                        app.logger.warning(f"Skipping line with incorrect date format: {line}")
    return studied_days

def save_studied_day(day):
    """Save studied day to a file if it's not already saved."""
    app.logger.info(f"Attempting to save studied day: {day}")
    file_path = os.path.join(os.getcwd(), 'studied_days.txt')
    studied_days = load_studied_days()
    if day not in studied_days:
        with open(file_path, 'a') as file:
            file.write(day.strftime("%Y-%m-%d") + '\n')
            app.logger.info(f"Saved studied day: {day}")

def print_calendars(year, studied_days):
    """Print the calendar with studied days marked."""
    months = []
    current_month = None
    for month in range(1, 13):
        cal = calendar.monthcalendar(year, month)
        month_data = {
            "name": calendar.month_name[month] + " " + str(year),
            "weeks": []
        }
        for week in cal:
            week_data = []
            for i, day in enumerate(week):
                if day == 0:
                    week_data.append(None)
                elif datetime.date(year, month, day) in studied_days:
                    week_data.append({"day": day, "studied": True})
                else:
                    week_data.append({"day": day, "studied": False})
            month_data["weeks"].append(week_data)
        if month == datetime.datetime.now().month:
            current_month = month_data
        else:
            months.append(month_data)
    return current_month, months

from flask import jsonify

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        if data.get('studied') == 'true':
            save_studied_day(datetime.date.today())
            return jsonify({'status': 'success'})
    studied_days = load_studied_days()
    current_month, months = print_calendars(datetime.datetime.now().year, studied_days)
    response = make_response(render_template('index.html', current_month=current_month, months=months))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

if __name__ == '__main__':
    app.run(debug=True)