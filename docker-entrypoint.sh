#!/bin/sh
set -e

# Using $3 since CMD is expended by shell as
# entrypoint /bin/sh -c CMD
# Using cut as $3 includes all the params...
cmd=$(echo $3 | cut -f1 -d' ')
if [ "$cmd" = 'pipelines' -a "$(id -u)" = '0' ]; then
    chown -R pipelines .
    exec gosu pipelines "$0" "$@"
fi

exec "$@"