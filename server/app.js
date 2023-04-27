const riot_api_key = 'RGAPI-be10431b-61b7-4dd2-8119-f89938c68597'

const port = 80;

const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const request = require('sync-request');
const urlencode = require('urlencode');
const morgan = require('morgan');

const app = express();

app.use(express.json()); 
app.use(express.urlencoded({ extended: false }));

app.use(morgan('dev'));

// app.use('/', express.static(path.join(__dirname, '../client/html/main.html')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/html/main.html'));
});

app.post('/search', (req, res) => {
  const username = req.body.username;
  var puuid;
  const find_PUUID_url = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + username + '?api_key=' + riot_api_key;
  request(find_PUUID_url, (err, res, body) => {
    const info_json = JSON.parse(body);
    // const key = Object.keys(info_json);
    // puuid = info_json[key]["id"];
    puuid = info_json.puuid;
    console.log(puuid);
  });
  res.send(puuid);
  console.log(puuid);
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