#!/bin/sh
set -e

# Using $3 since CMD is expended by shell as
# entrypoint /bin/sh -c CMD
if [ "$3" = 'pipelines' -a "$(id -u)" = '0' ]; then
    chown -R pipelines .
    exec gosu pipelines "$0" "$@"
fi

exec "$@"