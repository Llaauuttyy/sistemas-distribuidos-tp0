#!/bin/bash
MESSAGE="reply-to-me"

SERVER_RESPONSE=$(
    docker run --rm --network tp0_testing_net alpine sh -c "\
    echo '$MESSAGE' | nc server 12345 \
")

if [ "$SERVER_RESPONSE" = "$MESSAGE" ]; then
  echo "action: test_echo_server | result: success"
else
  echo "action: test_echo_server | result: fail"
fi