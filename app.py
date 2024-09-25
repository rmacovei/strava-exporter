from flask import Flask, request, redirect, session, url_for, jsonify
import requests
import os

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

    # Step 1: Fetch club members
    members_response = requests.get(
        f'https://www.strava.com/api/v3/clubs/{club_id}/members',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()
    
    print("HERE:---->")
    print(members_response)

    members_data = []

    # Step 2: Fetch activities for each member
    for member in members_response:
        athlete_id = member['id']
        member_name = member['firstname'] + " " + member['lastname']

        activities_response = requests.get(
            f'https://www.strava.com/api/v3/athletes/{athlete_id}/activities',
            headers={'Authorization': f'Bearer {access_token}'}
        ).json()

        print("HERE:---->")
        print(activities_response)
        # Step 3: Extract specific metrics for each member
        activities_data = []
        for activity in activities_response:
            activity_data = {
                'name': activity.get('name'),
                'distance': activity.get('distance'),  # Distance in meters
                'moving_time': activity.get('moving_time'),  # Time in seconds
                'elapsed_time': activity.get('elapsed_time'),  # Elapsed time in seconds
                'total_elevation_gain': activity.get('total_elevation_gain'),  # Elevation in meters
                'type': activity.get('type'),  # Type of activity (e.g., Run, Ride)
                'average_speed': activity.get('average_speed')  # Average speed in m/s
            }
            activities_data.append(activity_data)

        members_data.append({
            'member_name': member_name,
            'activities': activities_data
        })

    return jsonify(members_data)

if __name__ == '__main__':
    app.run(debug=True)
