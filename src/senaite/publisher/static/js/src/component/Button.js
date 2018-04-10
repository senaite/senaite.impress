import React from 'react';

class Button extends React.Component {

  handleClick = () => {
    console.info("Button " + this.props.name + " clicked...");
    this.props.clickHandler();
  }

  render() {
    return (
      <button uid={this.props.uid} name={this.props.name} onClick={this.props.onClick} className={this.props.className}>
        {this.props.title}
      </button>
    );
  }
}

export default Button;
