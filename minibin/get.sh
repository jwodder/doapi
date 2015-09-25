#!/bin/bash
curl -sSL -X GET \
	-H 'Content-Type: application/json' \
	-H "Authorization: Bearer $(cat ~/.doapi)" \
	"https://api.digitalocean.com${1:?Usage: $0 path}" | python -mjson.tool
