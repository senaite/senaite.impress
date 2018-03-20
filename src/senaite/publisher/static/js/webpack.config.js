const path = require('path');
const webpack = require('webpack');


module.exports = {
  entry: {
   "printview": path.resolve(__dirname, './src/printview.coffee'),
   "barcodes": path.resolve(__dirname, './src/barcodes.coffee')
  },

  output: {
    filename: 'senaite.publisher.[name].js',
    path: path.resolve(__dirname, './dist'),
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
