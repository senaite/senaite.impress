import React from 'react';

class DownloadButton extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <form method="POST" className={this.props.formClass}>

        <button type="submit" name={this.props.name} className={this.props.className}>
          {this.props.title}
        </button>

        <input type="hidden" name="template" value={this.props.context.template} />
        <input type="hidden" name="format" value={this.props.context.format} />
        <input type="hidden" name="orientation" value={this.props.context.orientation} />
        <input type="hidden" name="merge" value={this.props.context.merge} />
        <input type="hidden" name="html" value={this.props.html()} />
        <input type="hidden" name="submitted" value="1"/>

      </form>
    );
  }
}

export default DownloadButton;
