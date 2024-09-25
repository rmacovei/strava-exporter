from flask import Flask, request, redirect, session, url_for, jsonify
import requests
import os
import csv
from datetime import datetime, timedelta

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

    club_id = '1049135'  # Replace with your Strava club ID

    # Fetch public club activities
    activities_response = requests.get(
        f'https://www.strava.com/api/v3/clubs/{club_id}/activities',
        headers={'Authorization': f'Bearer {access_token}'},
        params={
            'before': datetime(2024, 6, 24),
            'after': datetime(2024, 8, 20)
        }
    ).json()

    activities_data = []
    allowed_activity_types = ['Hike', 'Run', 'Ride']

    # Extract relevant data from each activity
    for activity in activities_response:
        activity_type = activity.get('type')
        if activity_type in allowed_activity_types:  # Only include Hike, Run, Ride
            activity_data = {
                'athlete_name': activity.get('athlete', {}).get('firstname', '') + ' ' + activity.get('athlete', {}).get('lastname', ''),
                'activity_name': activity.get('name'),
                'distance': activity.get('distance'),  # Distance in meters
                'moving_time': activity.get('moving_time'),  # Time in seconds
                'elapsed_time': activity.get('elapsed_time'),  # Elapsed time in seconds
                'type': activity.get('type'),  # Type of activity (e.g., Run, Ride)
                'average_speed': activity.get('average_speed')  # Average speed in m/s
            }
            activities_data.append(activity_data)

    return jsonify(activities_data)

if __name__ == '__main__':
    app.run(debug=True)
