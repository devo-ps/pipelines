import React, { Component, PropTypes } from 'react';
import Task from '../Task/Task';
import {getAllPipelines} from '../../api';
import 'styles/main'
import DocumentTitle from 'react-document-title'



export default class Index extends Component {

  constructor(props) {
    super(props);
    this.state = {pipelines: [], title: 'Pipelines', loaded: false};
  }

  componentWillMount () {
    getAllPipelines()
    .then((data) => {
      this.setState({pipelines: data.tasks, title: data.title, loaded: true})
    })

  }

  render() {
    return (
      <DocumentTitle title={this.state.title}>
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
                if (item._error){
                    return (
                      <article className='item pipeline'>
                      <div className='notification warning'>
                        Error loading pipeline { item._filepath } : { item._error }
                      </div>
                      </article>
                      )
                }
                else {
                    return <Task key={index} task={item}/>;
                }

              })
              :
                (<div className='notification info'>No pipelines yet. <a href='https://github.com/Wiredcraft/pipelines/wiki' target='_blank'>See how to add a pipeline</a></div>)
            }
            </section>
            <small className="credit">Powered by <a href="http://github.com/Wiredcraft/pipelines/wiki" target="_blank">Pipelines</a></small>
          </div>
        </div>
      </section>
      </DocumentTitle>
    );
  }
};
