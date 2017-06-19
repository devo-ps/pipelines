import superagent from 'superagent'

//const API_URL = '/api/pipelines' // for DIST mode
const API_URL = `${__API_HOST__}/api/pipelines`

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
    return pipelines.map(function(item){
      if (!item.runs){
        item.runs = [];
      }
      return item
    })
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