const path = require('path');
const webpack = require('webpack');


module.exports = {
  entry: {
   "publish": path.resolve(__dirname, './src/publish.coffee')
  },

  output: {
    filename: 'senaite.publisher.[name].js',
    path: path.resolve(__dirname, './dist')
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: [/node_modules/],
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['react', 'env']
          }
        }
      }, {
        test: /\.coffee$/,
        exclude: [/node_modules/],
        use: {
          loader: 'coffee-loader',
          options: {}
        }
      }, {
        test: /\.css$/,
        use: [
          {loader: 'style-loader'},
          {
            loader: 'css-loader',
            options: {
              modules: true
            }
          }
        ]
      }
    ]
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery'
    })
  ],
};
