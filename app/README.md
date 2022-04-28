## Quick start

requirements:
- node v14+
- npx

```sh
$ make install
```

start dev server

```sh
$ make run
```

Go to [http://localhost:3000](http://localhost:3000)

if you what to change dev server port, binding address or change api server.

```
# more detail, see dev-server.js and Makefile
touch local.mk
echo "API_HOST := http://host:ip" >> local.mk
echo "DEV_SERVER_BIND := 0.0.0.0" >> local.mk
echo "DEV_SERVER_PORT := 5000" >> local.mk
```

### notes about dependency
