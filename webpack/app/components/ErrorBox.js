import React from 'react';

class ErrorBox extends React.Component {
  /** Error Box
   */

  constructor(props) {
    super(props);
  }

  render() {
    if (!this.props.error) {
      return null;
    }
    return (
      <div id="error" className="alert alert-danger">
        <h4 className="alert-heading">Ooops, an error occured</h4>
        <hr/>
        <pre>{this.props.error}</pre>
      </div>
    );
  }
}

export default ErrorBox;
