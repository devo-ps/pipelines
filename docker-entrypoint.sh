#!/bin/sh
set -e

if [ "$1" = 'pipelines' -a "$(id -u)" = '0' ]; then
    chown -R pipelines .
    exec gosu pipelines "$0" "$@"
fi

exec "$@"