import React, { Component, PropTypes } from 'react';
import Task from '../Task/Task';
import {getAllPipelines} from '../../api';
import 'styles/main'

export default class Index extends Component {

  constructor(props) {
    super(props);
    this.state = {pipelines: [], loaded: false};
  }

  componentWillMount () {
    getAllPipelines()
    .then((data) => {
      this.setState({pipelines: data, loaded: true})
    })

  }

  render() {
    return (
      <section className={!this.state.loaded?'loading':''} id='app'>
        <header id='header'>
          <div className='wrapper'>
            <nav className='links'>
              <a hred='http://github.com/Wiredcraft/pipelines/wiki' target='_blank'>Help</a>
            </nav>

            <h1>Pipelines</h1>
          </div>
        </header>
        <div id='main'>
          <div className='wrapper'>
            <header className='header'>
              <div className='controls'>
                <button className='button primary'>Add a pipeline</button>
              </div>

              <input type='text' placeholder='Filter by name' className='search'/>
            </header>
            <section className='body'>
            {
              this.state.pipelines && this.state.pipelines.length ?
              this.state.pipelines.map((item, index) => {
                return <Task key={index} task={item}/>;
              })
              :
                (<div className='notification info'>No pipelines yet. <a href='https://github.com/Wiredcraft/pipelines/wiki' target='_blank'>See how to add a pipeline</a></div>)
            }
            </section>
            <small className="credit">Powered by <a href="http://github.com/Wiredcraft/pipelines/wiki" target="_blank">Pipelines</a></small>
          </div>
        </div>
      </section>
    );
  }
};
