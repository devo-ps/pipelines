import React, { Component, PropTypes } from 'react'
import {Collapse} from 'react-bootstrap';
import LoadingIcon from '../LoadingIcon'
import * as API from '../../api'
import moment from 'moment';
var Highlight = require('react-syntax-highlight');

require('highlight.js/styles/default.css');

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
        triggers: []
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
        this.setState({
          open: true,
          task: task,
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

  selectLogsTab () {
    this.setState({ tab: 'logs' })
  }

  selectConfigTab () {
    this.setState({ tab: 'configuration' })
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
                className={ `status ${statusClass} active`}>
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
         <button className='icon previous'>
           <span className='svg icon' dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 15.4135,16.5841L 10.8275,11.9981L 15.4135,7.41207L 13.9995,5.99807L 7.99951,11.9981L 13.9995,17.9981L 15.4135,16.5841 Z '/></svg>"}}/>
           <span>Previous</span>
         </button>
         <span className='dropdown'>
           <div className='options'>
             { this.getRunsHtml(this.state.task.runs) }
           </div>
           <a className={`status ${statusClass}`}>{activeRunObj.status}	&middot; {activeRunObj && this.relativeTime(activeRunObj.start_time)}</a>
         </span>
         <button className='icon next'>
           <span className='svg icon'
                 dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 8.58527,16.584L 13.1713,11.998L 8.58527,7.41198L 9.99927,5.99798L 15.9993,11.998L 9.99927,17.998L 8.58527,16.584 Z '/></svg>"}}/>
           <span>Next</span>
         </button>
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
            ? <span className='svg icon' dangerouslySetInnerHTML={{__html:"<svg className='icon icon-checkmark'><use xlinkHref='#icon-checkmark'></use></svg>"}}/>
            : item.status === 'running'
              ? ''
              : <span className='svg icon' dangerouslySetInnerHTML={{__html:"<svg className='icon icon-cross'><use xlinkHref='#icon-cross'></use></svg>"}}/>
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
      var fields =  Object.keys(this.state.promptHolder).map(function(key){
        return (
          <span key={key}>
            <label>{key}</label>
            <input type='text' value={that.state.promptHolder[key]} onChange={that.handlePropFormChange.bind(that, key)}></input>
          </span>
        )
      });


      return (
        <div className={`prompt-tooltip ${this.state.showPrompt ? 'active' : 'inactive'}`}>
          <span>Please input fields:</span>
          <span>{fields}</span>
          <button onClick={this.onRun.bind(this, this.state.promptHolder)} >Run</button>
          <button onClick={::this.hidePrompt} >Cancel</button>
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
          return input.replace(regex, '<b style="color: gray">$1</b>')
        }
      };
      tabContent2 = (
        <div className='console' dangerouslySetInnerHTML={ {__html: highlight(this.state.logs[activeRunObj.id])} } >
        </div>
      );
    } else {
       tabContent =(
           <header className='toolbar'>
               <span className='status'>
                 webhooks: {this.state.triggers.map(function(item){ return <span>{item.webhook_id}</span>})}
               </span>
           </header>
         )
       tabContent2 = (<div className='console' >{this.state.task.raw }</div>);
    }

    return (
        <article
          className={`item pipeline ${activeRunObj.status} ${activ}`}
          onclick2='toggleItem(this)'
        >
          <header className='header' onClick={::this.toggleItem}>
            {this.getPromptFieldsHtml()}

            <button className='icon run' onClick={this.onRun.bind(this, undefined)}>
              <span className='svg icon' dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 7.99939,5.13684L 7.99939,19.1368L 18.9994,12.1368L 7.99939,5.13684 Z '/></svg>"}}/>
              <span>Run</span>
            </button>

            <h2>{this.props.task.slug}</h2>
            <span className='history'>
              { this.getRunHistoryPointers(this.props.task.runs) }
            </span>
          </header>

          <section className='body'>
            <nav className='tabs'>
              {/* < button className='icon fullscreen'>
                <span className='svg icon'
                    dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 9.49263,13.0931L 10.9068,14.5073L 6.41421,19L 10,19L 10,21L 3,21L 3,14L 5,14L 5,17.5858L 9.49263,13.0931 Z M 10.9069,9.49266L 9.49265,10.9069L 5,6.41422L 5,10L 3,10L 3,3.00001L 10,3L 10,5L 6.41421,5L 10.9069,9.49266 Z M 14.5074,13.0931L 19,17.5858L 19,14L 21,14L 21,21L 14,21L 14,19L 17.5858,19L 13.0932,14.5073L 14.5074,13.0931 Z M 13.0931,9.49265L 17.5858,5L 14,5L 14,3L 21,3L 21,10L 19,10L 19,6.41421L 14.5073,10.9069L 13.0931,9.49265 Z '/></svg>"}}/-->

                <span>Fullscreen</span>
              </button>
              */}

              <a className={`logs ${this.state.tab=='logs' ? 'active' : ''}`} onClick={::this.selectLogsTab}>Logs</a>
              <a className={`configuration ${this.state.tab=='configuration' ? 'active' : ''}`} onClick={::this.selectConfigTab}>Configuration</a>
            </nav>

            { tabContent }
            { tabContent2 }
          </section>
      </article>
    );
  }
};

