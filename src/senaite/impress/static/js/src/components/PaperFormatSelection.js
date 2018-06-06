import React from 'react';


class PaperFormatSelection extends React.Component {
  /** Ajax loaded selection for paper formats
   */

  constructor(props) {
    super(props);
    this.api = props.api;
    this.state = {
      formats: []
    };
  }

  fetch() {
    this.api.fetch_paperformats().then(data => {
      this.setState(
        {formats: data}
      );
    });
  }

  componentDidMount() {
    this.fetch();
  }

  buildOptions() {
    let options = [];
    let formats = this.state.formats;
    for (let [key, value] of Object.entries(formats)) {
      let title = `${value.name} (${value.page_width} x ${value.page_height}mm)`;
      options.push(
        <option key={key} value={value.format}>{title}</option>
      );
    }
    return options;
  }

  render() {
    return (
      <select value={this.props.value}
              onChange={this.props.onChange}
              name={this.props.name}
              className={this.props.className}>
        {this.buildOptions()}
      </select>
    );
  }
}

export default PaperFormatSelection;
