'use strict';

var webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
var config = require('./webpack.config.base.js');
var Path = require("path");

if (process.env.NODE_ENV !== 'test') {
  // see https://webpack.js.org/guides/hot-module-replacement
  config.entry = [
    `webpack-dev-server/client/index.js`,
    'webpack/hot/dev-server'
  ].concat(config.entry);
}

config.devtool = 'eval-cheap-module-source-map';

config.plugins = config.plugins.concat([
  new webpack.HotModuleReplacementPlugin(),
  new HtmlWebpackPlugin({
    title: 'Hot Module Replacement',
  }),
]);


module.exports = config;
