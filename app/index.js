'use strict';

var fs = require('fs');
var path = require('path');

var express = require('express');
var app = express();

var compress = require('compression');
var layouts = require('express-ejs-layouts');

app.set('layout');
app.set('view engine', 'ejs');
app.set('view options', {layout: 'layout'});
app.set('views', path.join(process.cwd(), '/server/views'));

app.use(compress());
app.use(layouts);
app.use('/client', express.static(path.join(process.cwd(), '/client')));

app.disable('x-powered-by');

var env = {
  production: process.env.NODE_ENV === 'production',
};

if (env.production) {
  Object.assign(env, {
    assets: JSON.parse(fs.readFileSync(path.join(process.cwd(), 'assets.json')))
  });
}

app.get('/*', function(req, res) {
  res.render('index', {
    env: env
  });
});

var port = Number(process.env.PORT || 3001);
app.listen(port, function () {
  console.log('server running at localhost:3001, go refresh and see magic');
});

if (env.production === false) {
  var webpack = require('webpack');
  var WebpackDevServer = require('webpack-dev-server');

  var webpackDevConfig = require('./webpack.config.development');

  const compiler = webpack(webpackDevConfig);
  const devServer = new WebpackDevServer({
    host: '0.0.0.0',
    port: 3000,
    // webSocketServer: 'sockjs',
    devMiddleware: {
      publicPath: '/client/',
      stats: true,
    },
    static: {
      directory: './',
    },
    client: false,
    // {
    //   webSocketURL: {
    //     hostname: '0.0.0.0',
    //     port: 3000,
    //   },
    // },
    // because we use custom dev server and already setup HMR
    // no need to turn on in options
    hot: false,

    // inline: true, // removed in webpack-dev-server v4
    historyApiFallback: true,
    headers: {
      'Access-Control-Allow-Origin': 'http://localhost:3001',
      'Access-Control-Allow-Headers': 'X-Requested-With'
    }
  }, compiler);

  (async () => {
    const err = await devServer.start();
    if (err) {
      console.log(err);
    }
    console.log('webpack dev server listening on localhost:3000');
  })();
}
