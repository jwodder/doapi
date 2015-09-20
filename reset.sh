#!/bin/bash
: ${DO_API_KEY:?Environment variable DO_API_KEY not defined}

DROPLET=???
IMAGE=ubuntu-12-04-x64

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

action $DROPLET '{"type":"rebuild","image":"'$IMAGE'"}'
