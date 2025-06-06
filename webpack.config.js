const Dotenv = require('dotenv-webpack');
const path = require('path');

module.exports = {
  entry: './script.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
  },
  plugins: [
    new Dotenv({
      systemvars: true, // Load system environment variables too
    })
  ],
};