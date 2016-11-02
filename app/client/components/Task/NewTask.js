import React, { Component, PropTypes } from 'react'
import {Collapse} from 'react-bootstrap';
import LoadingIcon from '../LoadingIcon'
import * as API from '../../api'
import moment from 'moment';
// var Highlight = require('react-syntax-highlight');

// require('highlight.js/styles/default.css');

var log = function(){
  // For easily enabling logs
  if (true){
    console.log.apply(console, arguments)
  }
}

export default class NewTask extends Component {

  static propTypes = {
    task: PropTypes.object
  };

  constructor(props) {
    super(props);
    var prompt = props.task.definition.prompt || {}
    this.state = {
        open: false,
        runTasks: [],
        runs: [],
        task: props.task,
        tab: 'logs',
        intervals: {},
        logs: {},
        promptHolder: prompt,
        triggers: [],
        activeRunId: undefined,
        fullscreen: false
    };
  }

  componentDidMount () {
    log('Component mounted', this.props)
    const {task} = this.props

    if (task.run_ids && task.run_ids.length > 0) {
      let temp = task.run_ids

//      Promise.all(temp.map((id, idx) => {
//        return API.getPipelineStatus(task.slug, id)
//          .then((result) => {
//            return {status: result.status, id: id}
//          })
//      }))
//      .then((result) => {
//        this.setState({
//          runs: result
//        })
//      })



      if (task.runs){
        var activeRunId = task.runs[0].id
        this.setState({activeRunId: activeRunId})
        this.refreshLogs(activeRunId)
        this.fetchTriggers(task.slug)
      } else {
        log('No runs', task)
      }
    }
  }

  refreshLogs(runId){

    return API.getPipelineLog(this.state.task.slug, runId)
      .then((result) => {
        log('Refreshed logs', runId)
        var logs = this.state.logs;
        logs[runId] = result.output;
        this.setState({logs: logs})
        return result.output;
      })
  }

  fetchTriggers(slug){
    return API.getTriggers(slug)
      .then((result) => {
        log('Fetched triggers for', slug)
        var triggers = result.triggers || []
        this.setState({triggers: triggers})
      })
  }

  getRunWithId (targetId) {
    var runs = this.state.task.runs;
    if (!runs){
      return undefined;
    }

    var matches = runs.filter(function(run){return run.id == targetId})
    if (matches.length > 0){
      return matches[0];
    }
    return undefined
  }

  onRun (params, ev) {
    ev.stopPropagation();
    log('onRun', params)
    if (Object.keys(this.state.promptHolder).length && !params){
      // Ask for params
      log('onRun ask for params', this.state.promptHolder, params)
      this.setState({showPrompt: true})
    }
    else {
        params = params || {}
        var task = this.state.task
        var this_run = {status: 'running', start_time: 'now', id: '0'}
        var runs = this.state.task.runs;
        runs.unshift(this_run)
        var that = this;
        var logs  = this.state.logs;
        logs['0'] = 'Loading...'
        this.setState({
          open: true,
          task: task,
          logs: logs,
          status: 'running',
          activeRunId: '0'

        })


        API.runPipeline(task.slug, params)
          .then((data) => {
            log('Pipeline run, new task id: ', data.task_id, task.slug)

            this_run.id = data.task_id;
            runs.unshift(this_run)
            that.setState({
              task: task,
              activeRunId: data.task_id
            })
            that.pollingLog(data.task_id)
            that.pollPipeline()
          })
        this.setState({showPrompt: false})
    }

  }

  toggleMenu () {
    this.setState({ open: !this.state.open })
  }

  toggleItem (item) {
    this.setState({ open: !this.state.open })
  }

  toggleFullscreen (item) {
    log('Toggle fullscreen', this.state.fullscreen)
    this.setState({ fullscreen: !this.state.fullscreen })
  }

  selectLogsTab () {
    this.setState({ tab: 'logs' })
  }

  selectConfigTab () {
    this.setState({ tab: 'configuration' })
  }

  selectWebhookTab () {
    console.log('wb')
    this.setState({ tab: 'webhook' })
  }

  pollPipeline(){
    if (this.pipelineInterval){
      log('Already polling')
    } else {
        function refreshPipelineInner () {
            const {task} = this.props
            var that = this;
            return API.getPipeline(task.slug)
              .then((result) => {
                console.log('Refreshed pipeline', task.slug, result)
                if (result){
                    this.setState({task: result})

                    var pipelineStatus = ''
                    result.runs.forEach(function(runObj){
                      if (that.state.intervals[runObj.id] != undefined && runObj.status != 'running'){
                        // Run finished, clear the timeout
                        clearTimeout(that.state.intervals[runObj.id])
                        delete that.state.intervals[runObj.id]
                      }
                      if (runObj.status == 'running'){
                        pipelineStatus = 'running'
                      }
                    })
                    this.setState({
                      status: pipelineStatus,
                      task: result
                    })
                }
              })
          }

      this.pipelineInterval = setInterval(refreshPipelineInner.bind(this), 4000)
    }
  }

  pollingLog (runId) {
    if (this.state.intervals[runId] != undefined){
      log('Already polling for logs for task.')
      return
    }
    function getLog(){
      this.refreshLogs(runId);
    }
    this.state.intervals[runId] = setInterval(getLog.bind(this), 2200)
    this.setState({intervals: this.state.intervals})
  }


  selectRun(runId) {
    this.setState({activeRunId: runId})
    this.refreshLogs(runId)
  }

  relativeTime(timestamp){
    if (timestamp == 'now') {
      return 'Now'
    }
    return moment(timestamp, "YYYY-MM-DDThh:mm:ss.SSSSSS").fromNow();
  }

  getRunHistoryPointers(runs){
    var that = this;
    return runs.slice(0,6).map(function(run){
      var status = run.status == 'success'? 'ok' : 'error';
      return <div className={`status ${status}`} key={run.id}><span>{run.status} &middot; { that.relativeTime(run.start_time)}</span></div>
    })
  }
  getRunsHtml(runs){
    var that = this;
    var runsHtml = '';

    if (this.state.task.runs && this.state.task.runs.length > 0){

          var runsHtml = runs.map((item, index) => {

            var statusClass = item.status == 'success'? 'ok' : 'error';
            return (
              <a
                key={'runs'+index}
                onClick={this.selectRun.bind(this, item.id)}
                className={ `status ${statusClass} ${item.id == that.state.activeRunId ? 'active': ''}`}>
                  {item.status}	&middot; { that.relativeTime(item.start_time) }
                </a>
            )
          });
      }
    return runsHtml;
  }
  getLogsToolbar(runsHtml) {

      var activeRunObj = this.getRunWithId(this.state.activeRunId) || {};
      log('aacc', activeRunObj)

      var statusClass = activeRunObj.status == 'success'? 'ok' : 'error';

     return (
       <header className='toolbar'>
         <span className='menu'>
           <div className='options'>
             { this.getRunsHtml(this.state.task.runs) }
           </div>
           <a className={`status ${statusClass}`}>{activeRunObj.status}	&middot; {activeRunObj && this.relativeTime(activeRunObj.start_time)}</a>
         </span>
         {/*
         <button className='icon previous'>
           <div className='svg' dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 15.4135,16.5841L 10.8275,11.9981L 15.4135,7.41207L 13.9995,5.99807L 7.99951,11.9981L 13.9995,17.9981L 15.4135,16.5841 Z '/></svg>"}}/>
           <span>Previous</span>
         </button>
         <button className='icon next'>
           <div className='svg'
                 dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 8.58527,16.584L 13.1713,11.998L 8.58527,7.41198L 9.99927,5.99798L 15.9993,11.998L 9.99927,17.998L 8.58527,16.584 Z '/></svg>"}}/>
           <span>Next</span>
         </button>
         */}
       </header>
     )


  }

  getPastRunHtml (runTasks, runs) {
    return runTasks.concat(runs).map((item, index) => {
      return (
        <li key={'runs'+index}
          onClick={this.refreshLogs.bind(this, item.id)}
          className={this.getRunWithId(this.state.activeRunId) === item.id ? 'active' : ''}>
          <span>
          {
            item.status === 'success'
            ? <span className='svg' dangerouslySetInnerHTML={{__html:"<svg className='icon icon-checkmark'><use xlinkHref='#icon-checkmark'></use></svg>"}}/>
            : item.status === 'running'
              ? ''
              : <span className='svg' dangerouslySetInnerHTML={{__html:"<svg className='icon icon-cross'><use xlinkHref='#icon-cross'></use></svg>"}}/>
           }
          </span>
          <span className='job-id'>{item.id}</span>
        </li>
      )
    })
  }


  handlePropFormChange(key, e) {
    var promptHolder = this.state.promptHolder;
    promptHolder[key] = e.target.value;
    this.setState({promptHolder: promptHolder})
  }

  getPromptFieldsHtml() {
    if (this.state.task.definition.prompt){
      var that = this;
      var fieldsHtml =  Object.keys(this.state.promptHolder).map(function(key){
        return (
          <div className="field" key={key}>
            <label>{key}</label>
            <input type='text' value={that.state.promptHolder[key]} onChange={that.handlePropFormChange.bind(that, key)}></input>
          </div>
        )
      });


      return (
        <div className={`overlay ${this.state.showPrompt ? 'active' : 'inactive'}`} onClick={ function(ev){ ev.stopPropagation();} }>
          <div className="modal">
            <header className="header">
              <a className="close" onClick={::this.hidePrompt}>Close</a>
              <h2>Fill in these values</h2>
            </header>
            <section className="body">
              <span>{ fieldsHtml }</span>
              <footer className="actions">
                <button className="button" onClick={::this.hidePrompt} >Cancel</button>
                <button className="button primary" onClick={this.onRun.bind(this, this.state.promptHolder)} >Run</button>
              </footer>
            </section>
          </div>
        </div>
      )
    }
  }

  hidePrompt(){
    this.setState({showPrompt: false})
  }
  render () {
    const {task} = this.props
    const {runTasks, runs} = this.state

    let pastJobs = this.getPastRunHtml(runTasks, runs)
    var activ = this.state.open ? 'active' : ''

    var tabContent = ''
    var tabContent2 = ''
    var activeRunObj = this.getRunWithId(this.state.activeRunId) || {}

    if (this.state.tab == 'logs'){

      tabContent = this.getLogsToolbar()
      function highlight(input){
        var regex = /(\d\d\d\d:\d\d:\d\d \d\d:\d\d:\d\d:)/g;
        if (input !== undefined){
          return input.replace(regex, '<time className="time">$1</time>')
        }
      };
      tabContent2 = (
        <div className='console' dangerouslySetInnerHTML={ {__html: highlight(this.state.logs[activeRunObj.id])} } >
        </div>
      );
    } else if (this.state.tab == 'webhook'){
      var webhookTabHtml;
      if (this.state.triggers[0] && this.state.triggers[0].webhook_id){
        webhookTabHtml = (
          <div className='content'>
            <p>Use this url to configure webhooks. For example, you can automate the deployment of your code by
            <a href='https://help.github.com/articles/about-webhooks/' target='_blank'>setting up your GitHub repo</a> to hit this URL whenever a new commit is pushed.</p>
            <div className='field'>
              <label>Webhook URL</label>
              <input type='text' readonly value="http://localhost:8888/webhook/{ this.state.triggers[0] && this.state.triggers[0].webhook_id ? this.state.triggers[0].webhook_id : '' }" />
            </div>
          </div>
        )
      } else {
        webhookTabHtml = (
          <div className='content'>
            <p className='empty'>This task has no webhook trigger. <a href='https://github.com/Wiredcraft/pipelines/wiki' target='_blank'>Read about how to add a webhook trigger</a>.</p>
          </div>
        )
      }
      tabContent2 = webhookTabHtml;
    }
     else {
       tabContent2 = (<div className='console' >{this.state.task.raw }</div>);
    }

    var fullscreenSvg;
    var fullscreenClass;
    if (this.state.fullscreen){
      fullscreenSvg = '<svg height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M0 0h24v24H0z" fill="none"/><path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/></svg>'
      fullscreenClass = 'fullscreen'
    } else {
      fullscreenSvg = '<svg height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M0 0h24v24H0z" fill="none"/><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>';
    }

    return (
        <article
          className={`item pipeline ${activeRunObj.status} ${activ} ${this.state.fullscreen?'fullscreen':''}`}
          onclick2='toggleItem(this)'
        >
          <header className='header' onClick={::this.toggleItem}>
            {this.getPromptFieldsHtml()}

            <button className='icon run' onClick={this.onRun.bind(this, undefined)}>
              <div className='svg' dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 7.99939,5.13684L 7.99939,19.1368L 18.9994,12.1368L 7.99939,5.13684 Z '/></svg>"}}/>
            </button>

            <h2>{this.props.task.slug}</h2>
            <span className='history'>
              { this.getRunHistoryPointers(this.props.task.runs) }
            </span>
          </header>

          <section className='body'>
            <nav className='tabs'>
              <button className='icon fullscreen' onClick={::this.toggleFullscreen}>
                <div className='svg'
                    dangerouslySetInnerHTML={{__html:fullscreenSvg}}/>
                <span>Fullscreen</span>
              </button>

              <a className={`logs ${this.state.tab=='logs' ? 'active' : ''}`} onClick={::this.selectLogsTab}>Logs</a>
              <a className={`configuration ${this.state.tab=='configuration' ? 'active' : ''}`} onClick={::this.selectConfigTab}>Configuration</a>
              <a className={`webhook ${this.state.tab=='webhook' ? 'active' : ''}`} onClick={::this.selectWebhookTab}>Webhook</a>
            </nav>

            { tabContent }
            { tabContent2 }
          </section>
      </article>
    );
  }
};
