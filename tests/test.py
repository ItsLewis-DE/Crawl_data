import requests

data = requests.get('https://api.open-meteo.com/v1/forecast').json()
print(data)
