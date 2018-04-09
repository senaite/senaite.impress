import React from 'react';


class ReportRow extends React.Component {

  constructor(props) {
    super(props);
    this.api = props.api;
    this.state = {
      model: {}
    };
  }

  fetch() {
    let endpoint = `get/${this.props.uid}`;
    this.api.get_json(endpoint).then(model => {
      this.setState(
        {model: model}
      );
    });
  }

  componentDidMount() {
    this.fetch();
  }

  buildColumns() {
    let columns = [];
    let fields = this.props.fields;
    fields.map(
      field =>
        columns.push(
          <td key={field.field}>{this.state.model[field.field]}</td>
        ));
    return columns;
  }

  render() {
    return (
      <tr>
        {this.buildColumns()}
      </tr>
    );
  }
}

export default ReportRow;
