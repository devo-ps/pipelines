import React, { Component, PropTypes } from 'react'
import {Collapse} from 'react-bootstrap';
import classnames from 'classnames'
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
    let runBtn = classnames({'disabled': this.state.running})

    return (
      <div className='wrapper'>
        <div className='task'>
            <div className='task-id'>{task.slug || '2344ddfs'}</div>
            <div className='task-name'>{task.name || 'Testing getpipeline.com'}</div>
            <div className='task-action'>
              {!this.state.status && <span onClick={::this.onRun} className={runBtn}><svg className='icon icon-circle-right'><use xlinkHref='#icon-circle-right'></use></svg></span>}
              {this.state.status === 'success' && <svg className='icon icon-checkmark'><use xlinkHref='#icon-checkmark'></use></svg>}
            </div>
        </div>
        <Collapse in={this.state.open}>
          <div className='details'>
          {this.state.taskLog}
          {this.state.running && <LoadingIcon /> }
          </div>
        </Collapse>
      </div>
    );
  }
};

