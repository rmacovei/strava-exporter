from flask import Flask, request, redirect, session, url_for, send_file
import requests
import os
import csv
from datetime import datetime, timedelta
import stravalib


app = Flask(__name__)
app.secret_key = os.urandom(24)

# Replace with your actual client_id, client_secret, and your app's redirect URI
CLIENT_ID = '113919'
CLIENT_SECRET = '3165002abb39098508df8f15ee15ceb7d608ae6a'
REDIRECT_URI = 'https://public-dale-strava-exporter-05c62d35.koyeb.app/callback'

@app.route('/')
def home():
    return '<a href="/authorize">Connect with Strava</a>'

@app.route('/authorize')
def authorize():
    return redirect(f'https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=read,read_all,profile:read_all,activity:read_all')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_response = requests.post(
        url='https://www.strava.com/oauth/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
    ).json()
    print("HERE:---->")
    print(token_response)
    session['access_token'] = token_response['access_token']
    return redirect(url_for('club_members'))

@app.route('/club_members')
def club_members():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('home'))

    # Initialize Strava client
    client = stravalib.Client()
    client.access_token = access_token

# Define the date range
    start_date = datetime(2024, 6, 24)
    end_date = datetime(2024, 8, 20)

    # Initialize a list to store activity data
    activity_data = []

    # Fetch activities within the date range
    activities = client.get_activities(after=start_date, before=end_date)
    print("HERE:---->")
    print(activities)
    
    for activity in activities:
        # Use get_activity to fetch additional details, including distance and time
        detailed_activity = client.get_activity(activity.id)

        # Convert distance from meters to kilometers, round to one decimal place, and format as a string
        distance_km = '{:.1f}'.format(detailed_activity.distance / 1000.0)

        activity_info = {
            'Activity Name': detailed_activity.name,
            'Distance (kilometers)': distance_km,
            'Activity Time': str(timedelta(seconds=int(detailed_activity.elapsed_time.total_seconds()))),
            'Activity Date': detailed_activity.start_date.strftime('%Y-%m-%d'),
            'Activity Type': detailed_activity.type
        }

        activity_data.append(activity_info)

    # Define the CSV file path (write to /tmp/ for Lambda)
    csv_file = '/tmp/strava_activity_data.csv'

   # Write the data to a CSV file
    with open(csv_file, 'w', newline='') as file:
        fieldnames = ['Activity Name', 'Distance (kilometers)', 'Activity Time', 'Activity Date', 'Activity Type']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write the activity data rows
        for data in activity_data:
            # Remove "meter" from distance field
            data['Distance (kilometers)'] = data['Distance (kilometers)'].replace(' meter', '')
            writer.writerow(data)

    # Return the CSV file to download
    return send_file(csv_file, as_attachment=True, attachment_filename='strava_activity_data.csv')


if __name__ == '__main__':
    app.run(debug=True)
