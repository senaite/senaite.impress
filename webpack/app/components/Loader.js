import React from 'react';

import "./Loader.css";


class Loader extends React.Component {
  /** Loader
   */

  constructor(props) {
    super(props);
  }

  render() {
    if (!this.props.loading) {
      return null;
    }
    return (
      <div id="loader" className="panel panel-default text-center">
        <div className="folding">
          <div className="sk-cube1 sk-cube"></div>
          <div className="sk-cube2 sk-cube"></div>
          <div className="sk-cube4 sk-cube"></div>
          <div className="sk-cube3 sk-cube"></div>
        </div>
        <div className="lead text-muted">{this.props.loadtext}</div>
      </div>
    );
  }
}

export default Loader;
