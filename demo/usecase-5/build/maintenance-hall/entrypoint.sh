#!/usr/bin/env bash
set -e

[ -z "${SITES}" ] && echo "SITES is not set" && exit 1

pid=0

# SIGTERM-handler
term_handler() {
    if [ $pid1 -ne 0 ]; then
        kill -SIGTERM "$pid1"
        wait "$pid1"
    fi
    if [ $pid2 -ne 0 ]; then
        kill -SIGTERM "$pid2"
        wait "$pid2"
    fi
    exit 143; # 128 + 15 -- SIGTERM
}

# setup handlers
# on callback, kill the last background process, which is `tail -f /dev/null` and execute the specified handler
trap 'kill ${!}; term_handler' SIGTERM
trap 'kill ${!}; term_handler' SIGINT

# run application
cd /web && /usr/local/bin/lanyon &
pid1="$!"
/maintenance-hall &
pid2="$!"

# wait forever
while true
do
    tail -f /dev/null & wait ${!}
done

