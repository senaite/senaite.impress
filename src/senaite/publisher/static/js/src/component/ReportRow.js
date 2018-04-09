import React from 'react';
import moment from 'moment';


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
    for (let field of fields) {
      let value = this.state.model[field.field];
      if (field.field.startsWith("Date")) {
        value = moment(value).startOf('day').fromNow();
      }
      columns.push(
        <td key={field.field}>{value}</td>
      );
    }
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
