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


module.exports = {
  mode: NODE_ENV === 'production' ? 'production' : 'development',

  entry: [
    // FIXME: see https://segmentfault.com/a/1190000021729561
    // may prefer babel-plugin-transform-runtime instead??
    // 'idempotent-babel-polyfill',
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
      helpers: 'client/helpers',
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
          "style-loader",
          "css-loader",
          {
            loader: "sass-loader",
            options: {
              sassOptions: {
                includePaths: require('bourbon').includePaths,
              }
            }
          }
        ]
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      },
      {
        test: /\.(js|jsx)$/,
        use: 'babel-loader',
        exclude: /node_modules/
      }
    ],
    noParse: /\.min\.js/
  },

  // NOTE: webpack 4, see https://webpack.js.org/configuration/performance/
  performance: {
    hints: false,
    maxEntrypointSize: 512000,
    maxAssetSize: 512000
  },
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
