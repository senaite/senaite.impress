import React from "react";

class Modal extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div id={this.props.id} className="modal fade" tabindex="-1"></div>
    );
  }
}

export default Modal;
