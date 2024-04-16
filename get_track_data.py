import os
import sys
import time
import json
import random
from datetime import datetime, timedelta
import requests
import pandas as pd

playlist_ids = [
    '37i9dQZEVXcDTxbvihAMNA', # my discover weekly
    '37i9dQZF1DX0kbJZpiYdZl', # hot hits USA
    '37i9dQZF1DX1lVhptIYRda', # hot country
    '37i9dQZF1DXcBWIGoYBM5M', # today's top hits
    '37i9dQZF1DX0XUsuxWHRQd', # rap caviar
    '37i9dQZF1EIcwI3ks67O1o', # my mood music mix
    '37i9dQZF1EIehlJXbuV04P', # my adventure mix
    '37i9dQZF1DWVqJMsgEN0F4', # alt now
    '37i9dQZF1DWYV7OOaGhoH0', # roots rising
]

this_dir = os.path.dirname(os.path.realpath(__file__))
past_schedule = json.load(open(os.path.join(this_dir, 'schedule.json'), 'r'))
past_tracks = set(sum([[x['track1Id'], x['track2Id']] for x in past_schedule], []))

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
        
def get_track_ids(playlist_id):
    playlist_resp = requests.get(
        f'https://api.spotify.com/v1/playlists/{playlist_id}',
        headers={'Authorization': f'Bearer {token["access_token"]}'}
    )
    return [
        i['track']['id']
        for i in playlist_resp.json()['tracks']['items']
        if not (i['track']['explicit'] or i['track']['id'] in past_tracks)
    ]

def update_schedule():
    track_ids = list(set(sum((get_track_ids(i) for i in playlist_ids), [])))
    track_ids = sorted(track_ids, key=lambda x: random.random())[:200]

    df = pd.DataFrame((get_track_info(id) for id in track_ids))
    df['track_id'] = df['uri'].apply(lambda x: x.split(':')[-1])
    df['artists'] = df['artists'].apply(lambda x: ', '.join(sorted([y['uri'] for y in x])))
    df = df.drop_duplicates(['artists']).sort_values(['playcount'], ascending=False).reset_index(drop=True)

    l1 = list(df[df.index % 2 == 0]['track_id'])
    l2 = list(df[df.index % 2 == 1]['track_id'])
    if len(l1) > len(l2):
        del l1[random.randint(0, len(l1)-1)]

    matchups = []
    while len(l1) > 0:
        i = random.randint(0, min(len(l1) - 1, 5))
        j = random.randint(0, min(len(l2) - 1, 5))
        matchups.append((l1[i], l2[j]) if random.random() > 0.5 else (l2[j], l1[i]))
        del l1[i]
        del l2[j]

    matchups.sort(key=lambda x: random.random())

    d = datetime.date(datetime.strptime(past_schedule[-1]['date'], r'%Y-%m-%d'))

    new_schedule = []
    for t1id, t2id in matchups:
        d += timedelta(days=1)
        new_schedule.append({
            'date': str(d),
            'track1Id': t1id,
            'track2Id': t2id,
        })

    with open(os.path.join(this_dir, 'schedule.json'), 'w') as f:
        json.dump(past_schedule + new_schedule, f)

def update_tracks():
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
    # just sending it with this mild jank: https://stackoverflow.com/a/52837375
    globals()[sys.argv[1]]()
