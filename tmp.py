import requests

r = requests.get("https://itunes.apple.com/lookup", params={"isbn": "9781718503540"})
print(r.text)
print(r.json())
