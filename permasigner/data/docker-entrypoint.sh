#!/bin/sh

ARGS=""
export VERSION=$(cat githash)

if [ ! -z "$URL" ]; then
    ARGS="$ARGS -u $URL"
fi

if [ ! -z "$DEBUG" ]; then
    ARGS="$ARGS -d"
fi

if [ ! -z "$BUNDLEID" ]; then
    ARGS="$ARGS -b $BUNDLEID"
fi

if [ ! -z "$NAME" ]; then
    ARGS="$ARGS -N $NAME"
fi

if [ ! -z "$MINVER" ]; then
    ARGS="$ARGS -m $MINVER"
fi

if [ ! -z "$LDIDFORK" ]; then
    ARGS="$ARGS -l $LDIDFORK"
fi

echo "Running Permasigner with args:$ARGS"
echo ""
python -u main.py $ARGS -n
