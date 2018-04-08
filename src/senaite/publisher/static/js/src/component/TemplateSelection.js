import React from 'react';


class TemplateSelection extends React.Component {
  /** Ajax loaded selection for templates
   */

  constructor(props) {
    super(props);
    this.api = props.api;
    this.state = {
      templates: []
    };
  }

  fetch() {
    this.api.fetch_templates().then(data => {
      this.setState(
        {templates: data}
      );
    });
  }

  componentDidMount() {
    this.fetch();
  }

  buildOptions() {
    let options = [];
    let templates = this.state.templates;
    templates.map(
      template =>
        options.push(
            <option key={template} value={template}>{template}</option>
        ));
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

export default TemplateSelection;
