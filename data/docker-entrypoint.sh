#!/bin/sh

ARGS=""

if [ ! -z "$URL" ]; then
    ARGS="$ARGS -u $URL"
fi

if [ ! -z "$DEBUG" ]; then
    ARGS="$ARGS -d"
fi

echo "Running Permasigner with args:$ARGS"
echo ""
python -u main.py $ARGS -n