import requests
import pandas as pd
import os  # Import the os module for directory handling

def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_data = auth_response.json()
    return auth_data['access_token']

def search_track(track_name, artist_name, token):
    query = f"{track_name} artist:{artist_name}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track"
    response = requests.get(url, headers={
        'Authorization': f'Bearer {token}'
    })
    json_data = response.json()
    try: 
        first_result = json_data['tracks']['items'][0]
        track_id = first_result['id']
        return track_id
    except (KeyError, IndexError):
        return None

def get_track_details(track_id, token):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    response = requests.get(url, headers={
        'Authorization': f'Bearer {token}'
    })
    json_data = response.json()
    image_url = json_data['album']['images'][0]['url']
    return image_url

# Replace these with your actual client ID an d client secret
client_id = '8ca38c45b33c4549a3cadb67a607db95'
client_secret = '8af3f99441334ad2b613bc7ea2a2f6e1' 

access_token = get_spotify_token(client_id, client_secret)

# Load the CSV file
df_spotify = pd.read_csv('/content/spotify-2023.csv', encoding='ISO-8859-1')

# Add a new column for image URLs
df_spotify['image_url'] = None

for i, row in df_spotify.iterrows():
    try:
        track_id = search_track(row['Track Name'], row['Artist Name'], access_token)
        if track_id:
            image_url = get_track_details(track_id, access_token)
            df_spotify.at[i, 'image_url'] = image_url
    except KeyError as e:
        print(f"Error processing row {i}: {e}")

# Specify a directory path where you have write permissions
output_directory = '/path/to/your/output/directory'

# Ensure the directory exists or create it if not
os.makedirs(output_directory, exist_ok=True)

# Save the updated DataFrame to a new CSV file
df_spotify.to_csv(os.path.join(output_directory, 'Spotify_updated.csv'), index=False)
