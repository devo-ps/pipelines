'use strict';

var webpack = require('webpack');
var config = require('./webpack.config.base.js');

var SaveAssetsJson = require('assets-webpack-plugin');
var FileSystem = require('fs')
var Path = require("path");

config.bail = true;
//config.debug = false;
config.profile = false;
config.devtool = '#source-map';

config.output = {
  path: Path.join(__dirname, '../pipelines/api/app_dist/client/dist'),
  pathinfo: true,
  publicPath: '/client/dist/',
  filename: 'bundle.min.js'
};

config.plugins = config.plugins.concat([
  new webpack.optimize.OccurrenceOrderPlugin(true),
//  new webpack.optimize.DedupePlugin(),
//  new webpack.optimize.UglifyJsPlugin({
//    output: {
//      comments: false
//    },
//    compress: {
//      warnings: false,
//      screw_ie8: true
//    }
//  }),
  new SaveAssetsJson({
    path: process.cwd(),
    filename: 'assets.json'
  }),
  new webpack.DefinePlugin({
    'process.env': {
      NODE_ENV: JSON.stringify('production')
    }
  }),
        function() {
            this.plugin("done", function(statsData) {
                var stats = statsData.toJson();

                if (!stats.errors.length) {
                    var inFileName = "index.tpl.html";
                    var outFileName = "../pipelines/api/app_dist/index.html";
                    var html = FileSystem.readFileSync(Path.join(__dirname, inFileName), "utf8");

                    var htmlOutput = html.replace(
                        /<script\s+src=(["'])(.+?)bundle\.js\1/i,
                        "<script src=$1$2" + stats.assetsByChunkName.main[0] + "$1");

                    FileSystem.writeFileSync(
                        Path.join(__dirname, outFileName),
                        htmlOutput);
                } else {
                    console.error('ERRORS', stats.errors)
                }

            });
        }
]);
//
//config.module.rules = config.module.loaders.concat([
//  {test: /\.jsx?$/, loaders: [ 'babel'], exclude: /node_modules/}
//]);

module.exports = config;
