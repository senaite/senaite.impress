import React from 'react';

class DownloadButton extends React.Component {

  handleClick = () => {
    console.info("Button " + this.props.name + " clicked...");
  }

  render() {
    return (
      <form method="POST" className={this.props.formClass}>

        <button type="button" name={this.props.name} onClick={this.props.onClick} className={this.props.className}>
          {this.props.title}
        </button>

        <input type="hidden" name="submitted" value="1"/>

      </form>
    );
  }
}

export default DownloadButton;
