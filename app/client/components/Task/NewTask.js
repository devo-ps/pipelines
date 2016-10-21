import React, { Component, PropTypes } from 'react'
import {Collapse} from 'react-bootstrap';
import LoadingIcon from '../LoadingIcon'
import * as API from '../../api'
import moment from 'moment';

export default class NewTask extends Component {

  static propTypes = {
    task: PropTypes.object
  };

  constructor(props) {
    super(props);
    this.state = {open: false, runTasks: [], historyTasks: [], task: props.task, tab: 'logs'};
    console.log('initial', this.state.task)
  }

  componentDidMount () {
    const {task} = this.props

    if (task.run_ids && task.run_ids.length > 0) {
      let temp = task.run_ids

      Promise.all(temp.map((id, idx) => {
        return API.getPipelineStatus(task.slug, id)
          .then((result) => {
            return {status: result.status, id: id}
          })
      }))
      .then((result) => {
        this.setState({
          historyTasks: result
        })
      })



      if (task.runs){
        var activeRunId = task.runs[0].id
        this.setState({activeRunId: activeRunId})
        API.getPipelineLog(task.slug, activeRunId)
        .then((result) => {
          var run = this.getRunWithId(activeRunId)
          if (run){
            run.log = result.output;
            this.setState({task: this.state.task})
          }

        })
      }
    }

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

  onRun (e) {

    const {task} = this.props
    let tmp = this.state.runTasks
    this.setState({ open: true})

    API.runPipeline(task.slug)
      .then((data) => {
        tmp.unshift({status: 'running', id: data.task_id})
        console.log('activeId', data.task_id)
        this.setState({
          activeRunId: data.task_id,
          running: true,
          runTasks: tmp
        })
        this.pollingLog()
        this.pollingPipeline()
      })
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

  pollingPipeline () {
    this.pipelineTimer = setTimeout(this.refreshPipeline.bind(this), 3000)
  }

  getStatus () {
    const {task} = this.props

    return API.getPipelineStatus(task.slug, this.state.activeRunId)
      .then((result) => {
        if (result && result.status === 'success') {
          let tmp = this.state.runTasks
          tmp[0].status = 'success'
          this.setState({
            running: false,
            status: 'success',
            runTasks: tmp
          })
        }
      })

  }

  refreshPipeline () {
    const {task} = this.props

    return API.getPipeline(task.slug)
      .then((result) => {
        this.setState({task: result})
      })
  }

  pollingLog () {
    if (this.state.running) {
      if (this.logTimer) {
        clearTimeout(this.logTimer)
      }
      this.logTimer = setTimeout(this.getLog.bind(this), 3000)
    }
  }

  getLog () {
    const {task} = this.props
    return API.getPipelineLog(task.slug, this.state.activeRunId)
      .then((result) => {
          var run = this.getRunWithId(this.state.activeRunId)
          console.log('got new log', run, result)
          if (run){
            run.log = result.output;
            this.setState({task: this.state.task})
          }

    })

  }

  getPastLog (taskId) {
    // console.log(taskId)
    this.setState({activeRunId: taskId})

    API.getPipelineLog(this.props.task.slug, taskId)
      .then((result) => {
        var run = this.getRunWithId(taskId)
        run.log = result.output;
        this.setState({task: this.state.task})
      })
  }

  relativeTime(timestamp){
    return moment(timestamp, "YYYY-MM-DDThh:mm:ss.SSSSSS").fromNow();
  }

  getRunHistoryPointers(runs){
    var that = this;
    return runs.map(function(run){
      var status = run.status == 'success'? 'ok' : 'error';
      return <div className={`status ${status}`} key={run.id}><span>{run.status} &middot; { that.relativeTime(run.start_time)}</span></div>
    })
  }

  render () {
    const {task} = this.props
    const {runTasks, historyTasks} = this.state

    let pastJobs = runTasks.concat(historyTasks).map((item, index) => {
      return (
        <li key={'historyTasks'+index}
          onClick={this.getPastLog.bind(this, item.id)}
          className={this.getRunWithId(this.state.activeRunId) === item.id ? 'active' : ''}>
          <span>
          {item.status === 'success'
            ? <svg className='icon icon-checkmark'><use xlinkHref='#icon-checkmark'></use></svg>
            : item.status === 'running' ? '' : <svg className='icon icon-cross'><use xlinkHref='#icon-cross'></use></svg>}
          </span>
          <span className='job-id'>{item.id}</span>
        </li>
      )
    })
    var activ = this.state.open ? 'active' : ''

    var tabContent = ''
    var tabContent2 = ''
    if (this.state.tab == 'logs'){
      var runsHtml = '';
      var that = this;
      var activeRunObj = this.getRunWithId(this.state.activeRunId);

      if (!activeRunObj){
        activeRunObj = {};
      }

      if (this.state.task.runs && this.state.task.runs.length > 0){

          var runsHtml = this.state.task.runs.map((item, index) => {

            var status = item.status == 'success'? 'ok' : 'error';
            return (
              <a
                key={'historyTasks'+index}
                onClick={this.getPastLog.bind(this, item.id)}
                className={ `status ${status} active`}>
                  {item.status}	&middot; { that.relativeTime(item.start_time) }
                </a>
            )
          });
      }
      var statusClass = activeRunObj.status == 'success'? 'ok' : 'error';
      tabContent = <header className='toolbar'>
                      <button className='icon previous'>
                        <span className='svg icon' dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 15.4135,16.5841L 10.8275,11.9981L 15.4135,7.41207L 13.9995,5.99807L 7.99951,11.9981L 13.9995,17.9981L 15.4135,16.5841 Z '/></svg>"}}/>
                         <span>Previous</span>
                       </button>
                      <span className='dropdown'>
                        <div className='options'>
                         {runsHtml}
                        </div>
                        <a className={`status ${statusClass}`}>{activeRunObj.status}	&middot; {activeRunObj && this.relativeTime(activeRunObj.start_time)}</a>
                      </span>
                      <button className='icon next'>
                        <span className='svg icon'
                            dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 8.58527,16.584L 13.1713,11.998L 8.58527,7.41198L 9.99927,5.99798L 15.9993,11.998L 9.99927,17.998L 8.58527,16.584 Z '/></svg>"}}/>
                        <span>Next</span>
                      </button>
                    </header>;
         function highlight(input){
            var regex = /(\d\d\d\d:\d\d:\d\d \d\d:\d\d:\d\d:)/g;
            if (input !== undefined){
            return input.replace(regex, '[$1]')
         }

       };
       tabContent2 = <div className='console' >{ activeRunObj.log }
        </div>;
   } else {

      tabContent2 = (<div className='console' >{ this.state.task.definition && JSON.stringify(this.state.task.definition, null, '  ') }</div>);

   }

    var activeRunObj = this.getRunWithId(this.state.activeRunId)
    if (!activeRunObj ) { activeRunObj  = {} }
    return (
      <article
        className={`item pipeline ${activeRunObj.status} ${activ}`}
        onclick2='toggleItem(this)'
      >
                  <header className='header' onClick={::this.toggleItem}>
                    <button className='icon run' onClick={::this.onRun}>
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
                      <button className='icon fullscreen'>
                        <span className='svg icon'
                            dangerouslySetInnerHTML={{__html:"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.1' baseProfile='full' width='24' height='24' viewBox='0 0 24.00 24.00' enable-background='new 0 0 24.00 24.00' xml:space='preserve'><path stroke-width='0.2' stroke-linejoin='round' d='M 9.49263,13.0931L 10.9068,14.5073L 6.41421,19L 10,19L 10,21L 3,21L 3,14L 5,14L 5,17.5858L 9.49263,13.0931 Z M 10.9069,9.49266L 9.49265,10.9069L 5,6.41422L 5,10L 3,10L 3,3.00001L 10,3L 10,5L 6.41421,5L 10.9069,9.49266 Z M 14.5074,13.0931L 19,17.5858L 19,14L 21,14L 21,21L 14,21L 14,19L 17.5858,19L 13.0932,14.5073L 14.5074,13.0931 Z M 13.0931,9.49265L 17.5858,5L 14,5L 14,3L 21,3L 21,10L 19,10L 19,6.41421L 14.5073,10.9069L 13.0931,9.49265 Z '/></svg>"}}/>

                        <span>Fullscreen</span>
                      </button>

                      <a className='logs' onClick={::this.selectLogsTab}>Logs</a>
                      <a className='configuration' onClick={::this.selectConfigTab}>Configuration</a>
                    </nav>

                    { tabContent }
                    { tabContent2 }
                  </section>
                </article>
    );
  }
};

