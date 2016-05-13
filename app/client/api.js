import superagent from 'superagent'

const API_URL = 'http://localhost:8888/api/pipelines'

function request(method, url) {
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
}

export function runPipeline(pipeline) {
  return new Promise((resolve, reject) => {
    request('POST', `/${pipeline}/run`)
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
    throw new Error("error occurs!")
  }
  return body
}