const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: {
    publish: path.resolve(__dirname, 'src/senaite/impress/static/js/src/publish.coffee')
  },
  output: {
    filename: 'senaite.impress.[name].js',
    path: path.resolve(__dirname, 'src/senaite/impress/static/js/scripts')
  },
  module: {
    rules: [
      {
        test: /\.coffee$/,
        exclude: [/node_modules/],
        use: ["babel-loader", "coffee-loader"]
      }, {
        test: /\.(js|jsx)$/,
        exclude: [/node_modules/],
        use: ["babel-loader"]
      }, {
        test: /\.css$/,
        use: ["style-loader", "css-loader"]
      }
    ]
  },
  plugins: [
    // https://webpack.js.org/plugins/provide-plugin/
    new webpack.ProvidePlugin({
      // $: 'jquery',
      // jQuery: 'jquery'
    })
  ],
  externals: {
    // https://webpack.js.org/configuration/externals
    jquery: '$'
  }
};
