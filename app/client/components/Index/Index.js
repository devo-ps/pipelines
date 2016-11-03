import React, { Component, PropTypes } from 'react';
import NewTask from '../Task/NewTask';
import {getAllPipelines} from '../../api';
import 'styles/main'

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
    console.log('rend', this.state.pipelines)
    if (this.state.pipelines.length === 0) {
      return (
        <p ref="empty loading">Loading...</p>
      );
    }

    return (
      <section>
        <header id='header'>
          <div className='wrapper'>
            <nav className='links'>
              <a hred='http://github.com/Wiredcraft/pipelines/wiki' target='_blank'>Help</a>
{/*}              <a onclick='showModal()' className='user'>
                <img src='assets/user.jpg' alt='hunvreus'/>
                Ronan
              </a>
*/}
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
                return <NewTask key={index} task={item}/>;
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


