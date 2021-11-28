import requests

payload = {'inUserName': 'redbus', 'inUserPass': 'redbus43211'}
url = 'https://tiket.sumberalam.net/'
req = requests.post(url, data=payload)

print(req)
