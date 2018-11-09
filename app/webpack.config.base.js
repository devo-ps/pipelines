var path = require('path');
var webpack = require('webpack');

var NODE_ENV = process.env.NODE_ENV;

var env = {
  production: NODE_ENV === 'production',
  staging: NODE_ENV === 'staging',
  test: NODE_ENV === 'test',
  development: NODE_ENV === 'development' || typeof NODE_ENV === 'undefined',
  api_host:  JSON.stringify(process.env.API_HOST || '')
};

Object.assign(env, {
  build: (env.production || env.staging)
});


var bourbonPaths = require('bourbon').includePaths

module.exports = {
  target: 'web',

  entry: [
    'idempotent-babel-polyfill',
    './client/main'
  ],

  output: {
    path: process.cwd(),
//    pathInfo: true,
    publicPath: '/client',
    filename: 'bundle.js'
  },

  resolve: {
    modules: [
      path.join(__dirname, ""),
      "web_modules",
      "node_modules",
      "client"
    ],
    extensions: ['.webpack.js', '.web.js', '.js', '.jsx', '.scss', '.css'],
    alias:  {
      styles: 'client/styles',
    }
  },

  plugins: [
    new webpack.DefinePlugin({
      __DEV__: env.development,
      __STAGING__: env.staging,
      __API_HOST__: env.api_host,
      __PRODUCTION__: env.production,
      __CURRENT_ENV__: '\'' + (NODE_ENV) + '\''
    })
  ],
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [
          {
            loader: "style-loader"
          }, {
            loader: "css-loader"
          }, {
            loader: "sass-loader",
            options: {
              includePaths: bourbonPaths
            }
          }
        ]
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      },
      {
        test: /\.json$/,
        use: 'json-loader'
      },
      {
        test: /\.(js|jsx)$/,
        use: 'babel-loader',
        exclude: /node_modules/
      }
    ],
    noParse: /\.min\.js/
  }
};

//config.module.rules.push(
//  {
//    test: /\.jsx?$/,
//    use: [
//      {
//        loaders: [ 'babel'],
//        options: {
//          exclude: /node_modules/
//        }
//      }
//    ]
//  }
//);

