const path = require("path");
const webpack = require("webpack");
const childProcess = require("child_process");

const CopyPlugin = require("copy-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");

const gitCmd = "git rev-list -1 HEAD -- `pwd`";
let gitHash = childProcess.execSync(gitCmd).toString().substring(0, 7);

const staticPath = path.resolve(__dirname, "../src/senaite/impress/static");

const devMode = process.env.mode == "development";
const prodMode = process.env.mode == "production";
const mode = process.env.mode;
console.log(`RUNNING WEBPACK IN '${mode}' MODE`);


module.exports = {
  // https://webpack.js.org/configuration/mode/#usage
  mode: mode,
  context: path.resolve(__dirname, "app"),
  entry: {
    main: [
      "./senaite.impress.coffee",
      "./senaite.impress.scss"
    ]
  },
  output: {
    // filename: `[name]-${gitHash}.js`,
    filename: "[name].js",
    path: path.resolve(staticPath, "bundles"),
    publicPath: "/++plone++senaite.impress.static/bundles"
  },
  module: {
    rules: [
      {
        test: /\.coffee$/,
        exclude: [/node_modules/],
        use: ["babel-loader", "coffee-loader"]
      },
      {
        test: /\.(js|jsx)$/,
        exclude: [/node_modules/],
        use: ["babel-loader"]
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"]
      },
      {
        // SCSS
        test: /\.s[ac]ss$/i,
        use: [
          {
            // https://webpack.js.org/plugins/mini-css-extract-plugin/
            loader: MiniCssExtractPlugin.loader,
          },
          {
            // https://webpack.js.org/loaders/css-loader/
            loader: "css-loader"
          },
          {
            // https://webpack.js.org/loaders/sass-loader/
            loader: "sass-loader"
          }
        ]
      }
    ]
  },
  optimization: {
    minimize: prodMode,
    minimizer: [
      // https://v4.webpack.js.org/plugins/terser-webpack-plugin/
      new TerserPlugin({
        exclude: /\/modules/,
        terserOptions: {
          // https://github.com/webpack-contrib/terser-webpack-plugin#terseroptions
          sourceMap: false, // Must be set to true if using source-maps in production
          format: {
            comments: false
          },
          compress: {
            drop_console: true,
            passes: 2,
          },
	      }
      }),
    ],
  },
  plugins: [
    // https://github.com/johnagan/clean-webpack-plugin
    new CleanWebpackPlugin(),
    // https://webpack.js.org/plugins/html-webpack-plugin/
    new HtmlWebpackPlugin({
      inject: false,
      filename:  path.resolve(staticPath, "resources.pt"),
      template: "resources.pt",
    }),
    // https://webpack.js.org/plugins/mini-css-extract-plugin/
    new MiniCssExtractPlugin({
      // N.B. use stable CSS name, because it is used in tinyMCE content as well
      //      -> see: `senaite.core.js`
      // filename: devMode ? "[name].css" : `[name]-${gitHash}.css`,
      filename: "[name].css"
    }),
    // https://webpack.js.org/plugins/copy-webpack-plugin/
    new CopyPlugin({
      patterns: [
        {
          // This CSS get hooked into WeasyPrint
          from: "../node_modules/bootstrap/dist/css/bootstrap.min.css",
          to: path.resolve(staticPath, "css")
        },
        {
          from: "../node_modules/@fortawesome/fontawesome-free",
          to: path.resolve(staticPath, "modules/fontawesome-free")
        },
      ]
    }),
    // https://webpack.js.org/plugins/provide-plugin/
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
    }),
  ],
  externals: {
    // https://webpack.js.org/configuration/externals
    react: "React",
    "react-dom": "ReactDOM",
    $: "jQuery",
    jquery: "jQuery",
  }
};
