#!/bin/bash
DO_API_KEY="$(cat ~/.doapi)"
DROPLET=${1:?Usage: $0 droplet size}
SIZE=${2:?Usage: $0 droplet size}

function action {
    droplet="$1"
    body="$2"
    actid=$(curl -X POST \
	    -H 'Content-Type: application/json' \
	    -H "Authorization: Bearer $DO_API_KEY" \
	    -d "$body" \
	    "https://api.digitalocean.com/v2/droplets/$droplet/actions" | \
	    jq '.action.id')
    status='"in-progress"'
    while [ "$status" = '"in-progress"' ]
    do status=$(curl -X GET \
		-H 'Content-Type: application/json' \
		-H "Authorization: Bearer $DO_API_KEY" \
		"https://api.digitalocean.com/v2/actions/$actid" | \
		jq '.action.status')
    done
    if [ "$status" = '"completed"' ]
    then return 0
    else return 1
    fi
}

set -ex

action $DROPLET '{"type":"shutdown"}' 

action $DROPLET '{"type":"resize","size":"'$SIZE'","disk":true}'

action $DROPLET '{"type":"power_on"}'
