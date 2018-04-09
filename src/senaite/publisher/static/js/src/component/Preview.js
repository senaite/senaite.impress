import React from 'react';


class Preview extends React.Component {
  /** Preview
   */

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div id={this.props.id}
           className={this.props.className}
           dangerouslySetInnerHTML={{__html: this.props.preview}}>
      </div>
    );
  }
}

export default Preview;
