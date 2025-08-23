#!/bin/bash
MESSAGE="reply-to-me"

SERVER_RESPONSE=$(
    docker run --rm --network tp0_testing_net alpine sh -c "\
    apk add --no-cache netcat-openbsd >/dev/null 2>&1 && \
    echo '$MESSAGE' | nc server 12345 \
")

echo "Server response: $SERVER_RESPONSE"

if [ "$SERVER_RESPONSE" = "$MESSAGE" ]; then
  echo "action: test_echo_server | result: success"
else
  echo "action: test_echo_server | result: fail"
fi