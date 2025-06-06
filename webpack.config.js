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
      systemvars: true, // Load system environment variables as well
      safe: true, // Load '.env.example' to verify the '.env' variables
      defaults: false // Don't load '.env.defaults'
    })
  ],
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
};