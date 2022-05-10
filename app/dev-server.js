'use strict';

const fs = require('fs');
const path = require('path');

const compress = require('compression');
const layouts = require('express-ejs-layouts');
const express = require('express');

const Webpack = require('webpack');
const WebpackDevServer = require('webpack-dev-server');

const webpackDevConfig = require('./webpack.config.development');

const devServerBind = process.env.DEV_SERVER_BIND || '0.0.0.0';
const devServerPort = Number(process.env.DEV_SERVER_PORT || 3000);

const compiler = Webpack(webpackDevConfig);
const devServer = new WebpackDevServer({
  host: devServerBind,
  port: devServerPort,
  devMiddleware: {
    publicPath: '/client/',
    stats: true,
  },
  static: {
    directory: './',
  },
  client: false,
  // because we use custom dev server and already setup HMR
  // no need to turn on in options
  hot: false,

  historyApiFallback: true,
  headers: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'X-Requested-With'
  }
}, compiler);

devServer.startCallback(() => {

  const app = devServer.app;
  app.set('layout');
  app.set('view engine', 'ejs');
  app.set('view options', {layout: 'layout'});
  app.set('views', path.join(process.cwd(), '/server/views'));

  app.use(compress());
  app.use(layouts);
  app.use('/client', express.static(path.join(process.cwd(), '/client')));

  app.disable('x-powered-by');

  const env = {
    production: process.env.NODE_ENV === 'production',
  };

  if (env.production) {
    Object.assign(env, {
      assets: JSON.parse(fs.readFileSync(path.join(process.cwd(), 'assets.json')))
    });
  }

  app.get('/*', function(req, res) {
    res.render('index', {
      env: env,
    });
  });

});
