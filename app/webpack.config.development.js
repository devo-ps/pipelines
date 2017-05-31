'use strict';

var webpack = require('webpack');
var config = require('./webpack.config.base.js');

if (process.env.NODE_ENV !== 'test') {
  config.entry = [
    'webpack-dev-server/client?http://localhost:3000',
    'webpack/hot/dev-server'
  ].concat(config.entry);
}

config.devtool = 'cheap-module-eval-source-map';

config.plugins = config.plugins.concat([
  new webpack.HotModuleReplacementPlugin()
]);

//config.module.rules.push(
//  {
//    test: /\.jsx?$/,
//    use: [
//      {
//        loader: 'react-hot-loader',
//        options: {
//          exclude: /node_modules/
//        }
//      },
////      {
////        loader: 'babel-loader',
//////        options: {
//////          exclude: /node_modules/
//////        }
////      },
//    ]
//  }
//);

module.exports = config;
