import React from 'react';

class Button extends React.Component {

  handleClick = () => {
    console.info("Button " + this.props.name + " clicked...");
    this.props.clickHandler();
  }

  componentDidMount() {
    console.info("Button did mount");

  }

  componentWillUnmount() {
    console.info("Button will unmount");

  }

  render() {
    return (
      <button onClick={this.handleClick} className={this.props.className}>
        {this.props.name}
      </button>
    );
  }
}

export default Button;
