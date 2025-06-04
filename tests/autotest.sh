#!/bin/bash

FILE_ORIGINAL="sent"
FILE_RECEIVED="received"
FILE_SIZE_MB=20
SERVER_PORT=$((RANDOM + 10000))

echo "Test started with file size $FILE_SIZE_MB MB"

dd if=/dev/urandom of="$FILE_ORIGINAL" bs=1M count=$FILE_SIZE_MB status=none

python ./src/server.py "$SERVER_PORT" "$FILE_ORIGINAL" &
SERVER_PID=$!

sleep 1

python ./src/client.py "$SERVER_PORT" "$FILE_RECEIVED"

wait $SERVER_PID

if cmp -s "$FILE_ORIGINAL" "$FILE_RECEIVED"; then
    echo "Test passed"
    EXIT_CODE=0
else
    echo "Wrong test"
    EXIT_CODE=1
fi

rm -f "$FILE_ORIGINAL" "$FILE_RECEIVED"

exit $EXIT_CODE
