'use strict';

var webpack = require('webpack');
var config = require('./webpack.config.base.js');

var SaveAssetsJson = require('assets-webpack-plugin');
var FileSystem = require('fs')
var Path = require("path");
const TerserPlugin = require('terser-webpack-plugin');

config.bail = true;
config.profile = false;
config.devtool = 'source-map';

config.output = {
  path: Path.join(__dirname, '../pipelines/api/app_dist/client/dist'),
  pathinfo: true,
  publicPath: '/client/dist/',
  filename: 'bundle.min.js'
};

config.optimization = {
  // OccurrenceOrderPlugin
  // see https://webpack.js.org/migrate/5/#update-outdated-options
  chunkIds: 'total-size',
  moduleIds: 'size',

  // webpackage v5, do not outpt LICENSE.txt
  minimizer: [new TerserPlugin({
    extractComments: false,
  })],
};
config.plugins = config.plugins.concat([
  new SaveAssetsJson({
    path: process.cwd(),
    filename: 'assets.json'
  }),
  new webpack.DefinePlugin({
    'process.env': {
      NODE_ENV: JSON.stringify('production')
    }
  }),
  new class {
    apply(compiler) {
      compiler.hooks.done.tap('my-plugin', statsData => {
        var stats = statsData.toJson();

        if (!stats.errors.length) {
          var inFileName = "index.tpl.html";
          var outFileName = "../pipelines/api/app_dist/index.html";
          var html = FileSystem.readFileSync(Path.join(__dirname, inFileName), "utf8");

          var htmlOutput = html.replace(
            /<script\s+src=(["'])(.+?)bundle\.js\1/i,
            "<script src=$1$2" + stats.assetsByChunkName.main[0] + "$1");

          FileSystem.writeFileSync(
            outFileName,
            htmlOutput);
        } else {
          console.error('ERRORS', stats.errors);
        }
      });
    }
  }(),
]);
//
//config.module.rules = config.module.loaders.concat([
//  {test: /\.jsx?$/, loaders: [ 'babel'], exclude: /node_modules/}
//]);

module.exports = config;
