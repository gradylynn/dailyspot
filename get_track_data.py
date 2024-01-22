import os
import time
import json
from datetime import datetime, timedelta
import requests
import pandas as pd

this_dir = os.path.dirname(os.path.realpath(__file__))

token = requests.post(
    'https://accounts.spotify.com/api/token',
    data={'grant_type': 'client_credentials'},
    auth=requests.auth.HTTPBasicAuth(
        os.environ['SPOTIFY_CLIENT_ID'],
        os.environ['SPOTIFY_CLIENT_SECRET']
    )
).json()

def get_track_info(track_id):
    track_resp = requests.get(
        f'https://api.spotify.com/v1/tracks/{track_id}',
        headers={'Authorization': f'Bearer {token["access_token"]}'}
    )
    time.sleep(.5)  # poor man's rate limiter
    playcount_resp = requests.get(
        f'https://api.t4ils.dev/albumPlayCount',
        params={'albumid': track_resp.json()['album']['id']}
    )
    for album_track in sum((d['tracks'] for d in playcount_resp.json()['data']['discs']), start=[]):
        if track_id in album_track['uri']:
            return album_track


def main():
    # planning to run this ~12am eastern
    tomorrow = datetime.date(datetime.utcnow())

    tracks_df = pd.DataFrame(
        json.load(open(os.path.join(this_dir, 'src', 'tracks.json'), 'r')),
        columns=['date', 'track1Id', 'track2Id', 'track1Playcount', 'track2Playcount']
    )
    schedule_df = pd.DataFrame(
        json.load(open(os.path.join(this_dir, 'schedule.json'), 'r'))
    )

    window_df = schedule_df[
        (schedule_df['date'] <= str(tomorrow + timedelta(days=5))) &
        (schedule_df['date'] >= str(tomorrow - timedelta(days=32)))
    ]
    window_df = window_df.merge(tracks_df, how='left', on=['date', 'track1Id', 'track2Id'])
    window_df['track1Playcount'] = window_df.apply(
        lambda x: x['track1Playcount'] if pd.notnull(x['track1Playcount']) and x['date'] <= str(tomorrow)
        else get_track_info(x['track1Id'])['playcount'],
        axis=1
    ).astype(int)
    window_df['track2Playcount'] = window_df.apply(
        lambda x: x['track2Playcount'] if pd.notnull(x['track2Playcount']) and x['date'] <= str(tomorrow)
        else get_track_info(x['track2Id'])['playcount'],
        axis=1
    ).astype(int)

    with open(os.path.join(this_dir, 'src', 'tracks.json'), 'w') as f:
        json.dump(window_df.sort_values('date', ascending=False).to_dict('records'), f)

if __name__ == '__main__':
    main()
