import React from 'react';


class ReportHTML extends React.Component {
  /** Rendered Reports HTML
   */

  render() {
    return (
      <div id={this.props.id}
           className={this.props.className}
           dangerouslySetInnerHTML={{__html: this.props.html}}>
      </div>
    );
  }
}

export default ReportHTML;
