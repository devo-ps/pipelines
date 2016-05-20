import React, { Component, PropTypes } from 'react'
import {Collapse} from 'react-bootstrap';
import LoadingIcon from '../LoadingIcon'
import * as API from '../../api'

export default class Task extends Component {

  static propTypes = {
    task: PropTypes.object
  };

  constructor(props) {
    super(props);
    this.state = {open: false};
  }

  onRun () {
    const {task} = this.props
    this.setState({ open: !this.state.open })

    API.runPipeline(task.slug)
      .then((data) => {
        console.log(data)
        this.setState({taskId: data.task_id, running: true})
        this.pollingLog()
        this.pollingStatus()
      })
  }

  toggleMenu () {
    this.setState({ open: !this.state.open })
  }

  pollingStatus () {
    if (this.state.running) {
      if (this.statusTimer) {
        clearTimeout(this.statusTimer)
      }
      this.statusTimer = setTimeout(this.getStatus.bind(this), 3000)
    }
  }

  getStatus () {
    const {task} = this.props

    return API.getPipelineStatus(task.slug, this.state.taskId)
      .then((result) => {
        if (result.status === 'success') {
          this.setState({running: false, status: 'success'})
        }
      })

  }

  pollingLog () {
    if (this.state.running) {
      if (this.logTimer) {
        clearTimeout(this.logTimer)
      }
      this.logTimer = setTimeout(this.getLog.bind(this), 1000)
    }
  }

  getLog () {
    const {task} = this.props
    return API.getPipelineLog(task.slug, this.state.taskId)
      .then((result) => {
        this.setState({taskLog: result.output})
      })

  }

  render () {
    const {task} = this.props
    let runBtn = <span onClick={::this.onRun}><svg className='icon icon-run'><use xlinkHref='#icon-play2'></use></svg></span>
    let runSpinnerBtn = <svg className='icon icon-running spinning'><use xlinkHref='#icon-spinner9'></use></svg>

    return (
      <div className='wrapper'>
        <div className='panel'>
          <div className='task panel-content'>
            <div className='task-action'>
              {!this.state.running && runBtn}
              {this.state.running && runSpinnerBtn}
            </div>
            <div className='task-summary'>
              <div className='title'>{task.slug || '2344ddfs'}</div>
              {this.state.running && <p><small>Task is running</small></p>}
              {this.state.status === 'success' && <p><small>Task run successfully</small></p>}
            </div>
          </div>
          <div className='panel-control'>
            {!this.state.open && <span onClick={::this.toggleMenu}><svg className='icon icon-menu'><use xlinkHref='#icon-menu'></use></svg></span>}
            {this.state.open && <span onClick={::this.toggleMenu}><svg className='icon icon-cross'><use xlinkHref='#icon-cross'></use></svg></span>}
          </div>
        </div>
        <Collapse in={this.state.open}>
          <div className='details'>
          {this.state.taskLog}
          {this.state.running && <span className='loading'><LoadingIcon /></span> }
          </div>
        </Collapse>
      </div>
    );
  }
};

