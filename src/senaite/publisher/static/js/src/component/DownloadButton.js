import React from 'react';

class DownloadButton extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <form method="POST" className={this.props.formClass}>

        <button type="submit" onClick={this.props.onClick} name={this.props.name} className={this.props.className}>
          {this.props.title}
        </button>
        <input type="hidden" name="submitted" value="1"/>

      </form>
    );
  }
}

export default DownloadButton;
