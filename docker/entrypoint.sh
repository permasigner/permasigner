#!/bin/sh

ARGS=""

if [ ! -z "$WINDOWS" ]; then
    export HOST_IS_WINDOWS=true
fi

if [ ! -z "$IPA" ]; then
    ARGS="$ARGS -p $IPA"
fi

if [ ! -z "$URL" ]; then
    ARGS="$ARGS -u $URL"
fi

if [ ! -z "$DEBUG" ]; then
    ARGS="$ARGS -d"
fi

if [ ! -z "$INSTALL" ]; then
    ARGS="$ARGS -i"
fi

if [ ! -z "$BUNDLEID" ]; then
    ARGS="$ARGS -b $BUNDLEID"
fi

if [ ! -z "$NAME" ]; then
    ARGS="$ARGS -n $NAME"
fi

if [ ! -z "$MINVER" ]; then
    ARGS="$ARGS -m $MINVER"
fi

if [ ! -z "$LDIDFORK" ]; then
    ARGS="$ARGS -l $LDIDFORK"
fi

if [ ! -z "$FOLDER" ]; then
    ARGS="$ARGS -f $FOLDER"
fi

if [ ! -z "$TCPRELAY" ]; then
    ARGS="$ARGS -t $TCPRELAY"
fi

if [ ! -z "$ENTITLEMENTS" ]; then
    ARGS="$ARGS -e $ENTITLEMENTS"
fi

if [ ! -z "$NO_LDID_CHECK" ]; then
    ARGS="$ARGS -z"
fi

if [ ! -z "$VERSION" ]; then
    ARGS="$ARGS -v"
fi

echo "Running Permasigner with args:$ARGS"
echo ""
poetry run permasigner $ARGS
