import React, { Component, PropTypes } from 'react';
import Task from '../Task/Task';
import {getAllPipelines} from '../../api';

export default class Index extends Component {

  constructor(props) {
    super(props);
    this.state = {pipelines: []};
  }

  componentWillMount () {
    getAllPipelines()
    .then((data) => {
      console.log(data)
      this.setState({pipelines: data})
    })
  }

  render() {
    if (this.state.pipelines.length === 0) {
      return (
        <p ref="empty">Index is empty.</p>
      );
    }

    return (
      <section>
        <h2>Pipeline tasks</h2>
        <ul ref="pipelineList" className="pipeline-list">
          {this.state.pipelines.map((item, index) => {
            return (
              <li key={index}><Task task={item}/></li>
            );
          })}
        </ul>
      </section>
    );
  }
};


