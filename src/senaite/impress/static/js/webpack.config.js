const path = require('path');
const webpack = require('webpack');


module.exports = {
  entry: {
    publish: path.resolve(__dirname, './src/publish.coffee')
  },
  output: {
    filename: 'senaite.impress.[name].js',
    path: path.resolve(__dirname, './dist')
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx|coffee)$/,
        exclude: [/node_modules/],
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['react', 'es2015', 'env'],
            plugins: ['transform-class-properties']
          }
        }
      }, {
        test: /\.coffee$/,
        exclude: [/node_modules/],
        use: [
          {
            loader: 'coffee-loader',
            options: {}
          }
        ]
      }, {
        test: /\.css$/,
        use: [
          {
            loader: 'style-loader'
          },
          {
            loader: 'css-loader'
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
