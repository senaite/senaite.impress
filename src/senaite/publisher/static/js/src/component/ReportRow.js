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
    for (let column of this.props.columns) {
      // extract the value from the model
      let model = this.state.model;
      let value = "";

      if (column.formatter) {
        value = column.formatter(column, model);
      } else {
        value = model[column.name];
      }
      if (React.isValidElement(value)) {
        value = <td key={column.name}>{value}</td>;
      } else {
        value = <td key={column.name} dangerouslySetInnerHTML={{__html: value}}></td>;
      }
      columns.push(value);
    }
    return columns;
  }

  render() {
    if (!this.state.model.title) {
      return null;
    }
    return (
      <tr>
        {this.buildColumns()}
      </tr>
    );
  }
}

export default ReportRow;
