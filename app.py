from flask import Flask, request, redirect, session, url_for, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Replace with your actual client_id, client_secret, and your app's redirect URI
CLIENT_ID = '113919'
CLIENT_SECRET = 'y3165002abb39098508df8f15ee15ceb7d608ae6a'
REDIRECT_URI = 'https://public-dale-strava-exporter-05c62d35.koyeb.app/callback'

@app.route('/')
def home():
    return '<a href="/authorize">Connect with Strava</a>'

@app.route('/authorize')
def authorize():
    return redirect(f'https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=read,read_all,profile:read_all')

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
    response = requests.get(
        f'https://www.strava.com/api/v3/clubs/{club_id}/members',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
