const port = 80;

const express = require('express');
const path = require('path');
const axios = require('axios');
const morgan = require('morgan');

require('dotenv').config();

const riot_api_key = process.env.riot_api_key;

let matches = {};
let info = {
  // name,
  // item0,
  // item1,
  // item2,
  // item3,
  // item4,
  // item5,

};

function sleep(ms) {
  const looptime = Date.now() + ms;
  while(Date.now() < looptime) {}
};

const app = express();

app.use(express.json()); 
app.use(express.urlencoded({ extended: false }));

app.use(morgan('dev'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/html/main.html'));
});

app.post('/search', async (req, res, next) => {
  const username = req.body.username;
  const puuid_url = `https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/${username}?api_key=${riot_api_key}`;
  let summoner_info, puuid;
  try {
    summoner_info = await axios.get(puuid_url);
    puuid = summoner_info.data.puuid;
  } catch(err) {
    next(err);
  };

  const matchid_url = `https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/${puuid}/ids?start=0&count=20&api_key=${riot_api_key}`;
  let matchid_all, matchids
  try {
    matchid_all = await axios.get(matchid_url);
    matchids = matchid_all.data;
  } catch(err) {
    next(err);
  };
  const matchid_length = matchids.length;

  let match_urls = [];

  for(let i=0; i<matchid_length; i++) {
    match_urls[i] = `https://asia.api.riotgames.com/lol/match/v5/matches/${matchids[i]}?api_key=${riot_api_key}`;
  }
  
  const requests = match_urls.map(url => axios.get(url));

  sleep(1000);

  try {
    await axios.all(requests)
    .then(res => {
      for(let i=0; i<matchid_length; i++) {
        matches[i] = res[i].data;
      }
    });
  } catch(err) {
    next(err)
  };

  // matches_json = JSON.stringify(matches);

  // console.log(`PUUID = ${puuid}`);
  // console.log(`matchids = ${matchids}`);

  // res.send(matches);
  res.redirect('/search');
});

app.get('/search', (req, res, next) => {
  res.send(matches);
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

// 서버 실행 --------------------------------------------------------------------------------------

app.listen(port, () => {
  console.log(`${port} start`);
});