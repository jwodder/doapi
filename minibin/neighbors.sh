#!/bin/bash
for drop
do curl -sSL -X GET \
	-H 'Content-Type: application/json' \
	-H "Authorization: Bearer $(cat ~/.doapi)" \
	"https://api.digitalocean.com/v2/droplets/$drop\neighbors" | \
   python -mjson.tool
done
