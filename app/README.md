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

make run
```

### notes about dependency

for more upgrading history, see `dependency-upgrade-history.txt`.

there were three frontend stylesheets dependencies in `client/app/styles/vendors` folder.
- normalize-scss
- bournbon
- egg (https://github.com/wiredcraft/egg)

first two are both an npm package. bournbon is actively maintained as of 2022-04. we just
remove both and change them to npm dependencies in `package.json`.

https://github.com/wiredcraft/egg is rather old, and a bower package, which is supported by yarn
through

```
{
  "dependencies": {
    "@bower_component/egg": "https://github.com/wiredcraft/egg",
  }
}
```

but it heavily depends on bournbon <= 4, whose various mixin are now deprecated. as we need to fix them,
considering https://github.com/wiredcraft/egg is not maintained anymore, we decide to keep this copy under
`client/app/styles/vendors/egg` and do fixes locally.

those mixins are now fixed by using standard css mixin in egg scss files, and processed by `postcss-loader` with `autoprefixer`.
see `webpack.config.base.js`.
