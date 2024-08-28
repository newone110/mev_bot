import requests
import json

url = "https://api.nowpayments.io/v1/conversion"

payload = json.dumps({
  "amount": "50",
  "from_currency": "sol",
  "to_currency": "usd"
})
headers = {
  'Authorization': 'Bearer {{eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQ5NjE2NzgzNTkiLCJpYXQiOjE3MjM4NzAyMTksImV4cCI6MTcyMzg3MDUxOX0.t0KnsuAdXBauOqyJc77aL5lc-YoFaSV6KplWZ-gKwF4}}',
  'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
