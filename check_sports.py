import requests
import json
API_KEY="eb18d651138a0126bd68a2cded55e1b8"
url = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
response = requests.get(url)
if response.status_code == 200:
    for s in response.json():
        if 'tennis' in s['key'] or 'basketball' in s['key'] or 'soccer' in s['key']:
            print(f"{s['group']} - {s['title']}: {s['key']}")
else:
    print("Error:", response.status_code)
