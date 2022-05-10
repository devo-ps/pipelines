API_HOST := http://127.0.0.1:8888
DEV_SERVER_PORT := 3000
DEV_SERVER_BIND := 0.0.0.0

-include local.mk

install:
	npx yarn --ignore-platform

run:
	API_HOST=${API_HOST} DEV_SERVER_PORT=${DEV_SERVER_PORT} DEV_SERVER_BIND=${DEV_SERVER_BIND} \
		npx yarn start
