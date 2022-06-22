import superagent from 'superagent';

// used for local dev, on remote host
let API_URL = `${__API_HOST__}/api/pipelines`;

// NOTE: this is to support hosting pipelines at different path
// not just root like http://example.com/
// used for production, there will be an #js-entry element
// with data-api-base property, provisioned by backend
// giving the exact API_URL
const entry = document.querySelector('#js-entry');
if (!!entry) {
  API_URL = entry.dataset.apiBase.replace(/\/+$/g, '');
}

// console.log(`API_URL: ${API_URL}`);

function request(method, url, body) {
  return superagent(method, `${API_URL}${url}`)
    .set('Accept', 'application/json')
}

export function getAllPipelines() {
  return new Promise((resolve, reject) => {
    request('GET', '/')
    .end((err, res) => {
      if (err) return reject(err)
      resolve(res.text)
    })
  })
  .then(bodyParser)
  .then(function(pipelines){
    pipelines.tasks.map(function(item){
      if (!item.runs){
        item.runs = [];
      }
      return item
    })
    return pipelines
  })
}

export function runPipeline(pipeline, params) {
  console.log('api.runPipeline', pipeline, params)
  params = params || {}
  return new Promise((resolve, reject) => {
    request('POST', `/${pipeline}/run`)
    .send({'prompt': params})
    .end((err, res) => {
      if (err) return reject(err)
      resolve(res.text)
    })
  })
  .then(bodyParser)
}

export function getPipelineStatus(pipeline, taskId) {
  return new Promise((resolve, reject) => {
    request('GET', `/${pipeline}/${taskId}/status`)
    .end((err, res) => {
      if (err) return reject(err)
      resolve(res.text)
    })
  })
  .then(bodyParser)
}

export function getPipeline(pipeline) {
  return new Promise((resolve, reject) => {
    request('GET', `/${pipeline}/`)
    .end((err, res) => {
      if (err) return reject(err)
      resolve(res.text)
    })
  })
  .then(bodyParser)
}

export function getTriggers(pipeline) {
  return new Promise((resolve, reject) => {
    request('GET', `/${pipeline}/triggers`)
    .end((err, res) => {
      if (err) return reject(err)
      resolve(res.text)
    })
  })
  .then(bodyParser)
}


export function getPipelineLog(pipeline, taskId) {
  return new Promise((resolve, reject) => {
    request('GET', `/${pipeline}/${taskId}/log`)
    .end((err, res) => {
      if (err) return reject(err)
      resolve(res.text)
    })
  })
  .then(bodyParser)
}

const bodyParser = res => {
  let body
  try {
    body = JSON.parse(res)
  } catch (err) {
    console.log('Error parsing response', err);
    throw err;
  }
  return body
}
