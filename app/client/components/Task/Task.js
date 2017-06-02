import React, { Component, PropTypes } from 'react'
import * as API from '../../api'
import moment from 'moment';
import { processPromptDef } from 'helpers/prompt'
import { relativeTime } from 'helpers/time'
import { highlightLog } from 'helpers/log'
import EnterFullScreen from '../svg/EnterFullScreen'
import LeaveFullScreen from '../svg/LeaveFullScreen'

const log = console.log

export default class Task extends Component {

  static propTypes = {
    task: PropTypes.object
  };

  constructor(props) {
    super(props);

    const prompt = processPromptDef(props.task.definition.prompt)
    this.state = {
        open: false,
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


  componentDidMount() {
    log('Component mounted', this.props)
    const {task} = this.props
    this.fetchTriggers(task.slug)
    if (task.run_ids && task.run_ids.length > 0) {
      if (task.runs){
        var activeRunId = task.runs[0].id
        this.setState({activeRunId: activeRunId})
        this.refreshLogs(activeRunId)
      } else {
        log('No runs', task)
      }
    }
  }

  refreshLogs(runId) {
    return API.getPipelineLog(this.state.task.slug, runId)
      .then((result) => {
        log('Refreshed logs', runId)
        var logs = this.state.logs;
        logs[runId] = result.output;
        this.setState({logs: logs})
        return result.output;
      })
  }

  fetchTriggers(slug) {
    log('Fetch Triggers', slug)
    return API.getTriggers(slug)
      .then((result) => {
        log('Fetched triggers for', slug)
        const triggers = result.triggers || []
        this.setState({triggers: triggers})
      })
  }

  getRunWithId(targetId) {
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

  onRun(params, ev) {
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
            that.refreshLogs(data.task_id)
            that.pollingLog(data.task_id)
            that.pollPipeline()
          })
        this.setState({showPrompt: false})
    }
  }

  toggleMenu() {
    this.setState({ open: !this.state.open })
  }

  toggleItem(item) {
    if (!this.state.fullscreen){
      this.setState({ open: !this.state.open })
    }
  }

  toggleFullscreen(item) {
    this.setState({ fullscreen: !this.state.fullscreen })
  }

  selectLogsTab() {
    this.setState({ tab: 'logs' })
  }

  selectConfigTab() {
    this.setState({ tab: 'configuration' })
  }

  selectWebhookTab() {
    this.setState({ tab: 'webhook' })
  }

  pollPipeline() {
    if (this.pipelineInterval){
      log('pollPipeline: Already polling')
    } else {
        var pipelineInterval;
        function refreshPipelineInner () {
            const {task} = this.props
            var that = this;
            return API.getPipeline(task.slug)
              .then((result) => {
                log('Refreshed pipeline', task.slug, result)
                if (result){
                    this.setState({task: result})

                    var pipelineStatus = ''
                    result.runs.forEach(function(runObj){
                      if (that.state.intervals[runObj.id] != undefined && runObj.status != 'running'){
                        // Run finished, clear the timeout
                        clearTimeout(that.state.intervals[runObj.id])
                        clearTimeout(pipelineInterval)
                        that.refreshLogs(runObj.id) // Fetch one last time
                        delete that.state.intervals[runObj.id]
                      }
                      if (runObj.status == 'running'){
                        pipelineStatus = 'running'
                      }
                    })
                    that.setState({
                      status: pipelineStatus,
                      task: result
                    })
                }
              })
          }

      pipelineInterval = setInterval(refreshPipelineInner.bind(this), 1500)
    }
  }

  pollingLog(runId) {
    if (this.state.intervals[runId] != undefined){
      log('pollingLog: Already polling for logs for task.')
      return
    }
    const getLog = () => {
      this.refreshLogs(runId);
    }
    this.state.intervals[runId] = setInterval(getLog, 2200)
    this.setState({intervals: this.state.intervals})
  }


  selectRun(runId) {
    this.setState({activeRunId: runId})
    this.refreshLogs(runId)
  }


  getRunHistoryPointers(runs){
    if (!runs || runs.length == 0) {
      return <div className='empty'>No runs yet</div>
    }
    return runs.slice(0,6).map(run => {
      const status = run.status == 'success'? 'ok' : 'error';
      return (
        <div className={`status ${status}`} key={run.id}>
          <span>{run.status} &middot; { relativeTime(run.start_time)}</span>
        </div>
      )
    })
  }

  getRunsHtml(runs) {
    var runsHtml = '';

    if (runs && runs.length > 0){
      const runsHtml = runs.map((item, index) => {
        if (!item){
          console.log('Undefined run', runs)
          return
        }

        const statusClass = item.status == 'success'? 'ok' : 'error';

        return (
          <a
            key={'runs'+index}
            onClick={this.selectRun.bind(this, item.id)}
            className={ `status ${statusClass} ${item.id == this.state.activeRunId ? 'active': ''}`}
          >
            {item.status}	&middot; { relativeTime(item.start_time) }
          </a>
        )
      });
    }
    return runsHtml;
  }

  getLogsToolbar(runsHtml) {
    var activeRunObj = this.getRunWithId(this.state.activeRunId) || {};
    var statusClass = activeRunObj.status == 'success'? 'ok' : 'error';

     return (
       <header className='toolbar'>
         <span className='menu'>
           <div className='options'>
             { this.getRunsHtml(this.state.task.runs) }
           </div>
           <a className={`status ${statusClass}`}>{activeRunObj.status}	&middot; {activeRunObj && relativeTime(activeRunObj.start_time)}</a>
         </span>
       </header>
     )
  }

  getPastRunHtml(runs) {
    return runs.map((item, index) => {
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
      var prompt_def = this.state.task.definition.prompt;
      var fieldsHtml =  Object.keys(prompt_def).map(function(key){
        if (typeof prompt_def[key] === 'string' || prompt_def[key] instanceof String){
            return (
              <div className="field" key={key}>
                <label>{key}</label>
                <input type='text' value={that.state.promptHolder[key]} onChange={that.handlePropFormChange.bind(that, key)}></input>
              </div>
            )
        } else {
            console.log('getPromptFieldsHtml', that.state.promptHolder)
            if (prompt_def[key]['type'] == 'select'){

                var optionsHtml = prompt_def[key]['options'].map(function(option){
                    return <option key={option}>{ option }</option>
                })

                return (
                  <div className="field" key={key}>
                    <label>{key}</label>
                        <span className='select'>
                            <select onChange={that.handlePropFormChange.bind(that, key)} value={that.state.promptHolder[key]}>
                                { optionsHtml }
                            </select>
                        </span>
                  </div>
                )
            }
        }

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

  hidePrompt() {
    this.setState({showPrompt: false})
  }

  render() {
    const {task} = this.props

    let pastJobs = this.getPastRunHtml(this.state.task.runs)
    var activ = this.state.open ? 'active' : ''

    var tabContent = ''
    var tabContent2 = ''
    var activeRunObj = this.getRunWithId(this.state.activeRunId) || {}

    if (this.state.tab == 'logs'){
      if (this.state.task.runs && this.state.task.runs.length){
        tabContent = this.getLogsToolbar()

        tabContent2 = (
        <div className='console' dangerouslySetInnerHTML={ {__html: highlightLog(this.state.logs[activeRunObj.id] || 'No logs yet')} } >
        </div>
        );
      } else {
        tabContent2 = (
          <div className='content'>
            <div className='notification info'>You haven't run this pipeline yet. Click the "Run" button at the top or <a href='https://github.com/Wiredcraft/pipelines' target='_blank'>see how to trigger pipelines</a></div>
         </div>
         )
      }

    } else if (this.state.tab == 'webhook'){
      var webhookTabHtml;
      if (this.state.triggers[0] && this.state.triggers[0].webhook_id){
        webhookTabHtml = (
          <div className='content'>
            <p>Use this url to configure webhooks. For example, you can automate the deployment of your code by <a href='https://help.github.com/articles/about-webhooks/' target='_blank'> setting up your GitHub repo</a> to hit this URL whenever a new commit is pushed.</p>
            <div className='field'>
              <label>Webhook URL</label>
              <input type='text' readOnly value={`${window.location.protocol}//${window.location.host}/api/webhook/${ this.state.triggers[0] && this.state.triggers[0].webhook_id ? this.state.triggers[0].webhook_id : '' }`} />
            </div>
          </div>
        )
      } else {
        webhookTabHtml = (
          <div className='content'>
            <div className='notification info'>This task has no webhook trigger. <a href='https://github.com/Wiredcraft/pipelines/wiki' target='_blank'>Read about how to add a webhook trigger</a>.</div>
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
        >
          <header className='header' onClick={::this.toggleItem}>
            {this.getPromptFieldsHtml()}

            <button className='icon run' onClick={this.onRun.bind(this, undefined)}>
              <div className='svg' dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 7.99939,5.13684L 7.99939,19.1368L 18.9994,12.1368L 7.99939,5.13684 Z '/></svg>"}}/>
            </button>

            <h2>{this.state.task.definition.name ? this.state.task.definition.name : this.state.task.slug}</h2>
            <span className='history'>
              { this.getRunHistoryPointers(this.state.task.runs) }
            </span>
          </header>

          <section className='body'>
            <nav className='tabs'>
              <button className='icon fullscreen' onClick={::this.toggleFullscreen}>
                <div className='svg'>
                  { this.state.fullscreen ? <LeaveFullScreen /> : <EnterFullScreen /> }
                </div>
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
