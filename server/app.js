const port = 80;
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser')
const morgan = require('morgan');

const app = express();

// app.use(morgan('dev'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/html/main.html'));
});

app.post('/search', (req, res) => {
  // let username = req.body.username;
  res.send(req.body);
});

// 404 미들웨어 ----------------------------------------------------------------------------------
app.use((req, res, next) => {
  const url = decodeURIComponent(req.url);
  const error = new Error(`${req.method} ${url} doesn't exist (404)`);
  error.status = 404;
  next(error);
});

// 에러 처리 미들웨어 -----------------------------------------------------------------------------
app.use((err, req, res, next) => {
  const status = (err.status || 500);
  if(status == 404) {
    res.status(status).sendFile(path.join(__dirname, 'error/404.html'));
    console.log(err.message);
  } else {
    res.status(status).sendFile(path.join(__dirname, 'error/500.html'));
    console.log(err.message || 'Error', '(500)');
  };
});

app.listen(port, () => {
  console.log(`${port} start`);
});