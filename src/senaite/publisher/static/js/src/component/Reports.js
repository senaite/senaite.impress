import React from 'react';


class Reports extends React.Component {
  /** Reports
   */

  constructor(props) {
    super(props);
  }

  componentDidUpdate() {
    console.info("Reports::componentDidUpdate:");
  }

  render() {
    return (
      <div id={this.props.id}
           className={this.props.className}
           dangerouslySetInnerHTML={{__html: this.props.html}}>
      </div>
    );
  }
}

export default Reports;
