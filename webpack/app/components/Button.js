import React from 'react';

class Button extends React.Component {

  handleClick = () => {
    console.info("Button " + this.props.name + " clicked...");
    this.props.clickHandler();
  }

  render() {
    return (
      <button uid={this.props.uid} name={this.props.name} title={this.props.title} url={this.props.url} onClick={this.props.onClick} className={this.props.className}>
        <span dangerouslySetInnerHTML={{__html: this.props.text || this.props.title}}></span>
      </button>
    );
  }
}

export default Button;
