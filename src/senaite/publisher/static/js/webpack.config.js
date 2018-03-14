const path = require('path');

module.exports = {
    entry: path.resolve(__dirname, './src/printview.js'),
    output: {
        path: path.resolve(__dirname, './dist'),
        filename: 'senaite.publisher.printview.js',
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
            }
        ]
    }
};
