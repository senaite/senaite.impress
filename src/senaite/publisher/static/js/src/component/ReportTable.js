import React from 'react';
import ReportRow from "./ReportRow.js";


class ReportTable extends React.Component {

  constructor(props) {
    super(props);
    this.api = props.api;
    this.state = {
      fields: [
        {
          field: "title",
          title: "Title"
        },
        {
          field: "ContactFullName",
          title: "Contact"
        },
        {
          field: "ContactEmail",
          title: "Email"
        },
        {
          field: "ClientTitle",
          title: "Client"
        },
        {
          field: "DateReceived",
          title: "Date Received"
        }
      ]
    };
  }

  buildHeader() {
    let header = [];
    let fields = this.state.fields;
    fields.map(
      field =>
        header.push(
          <th key={field.field}>{field.title}</th>
        ));
    return header;
  }

  buildRows() {
    let rows = [];
    let uids = this.props.uids;
    uids.map(
      uid =>
        rows.push(
          <ReportRow uid={uid} fields={this.state.fields} api={this.api} key={uid} />
        ));
    return rows;
  }

  render() {
    return (
      <table className="table table-condensed">
        <thead>
          <tr>
            {this.buildHeader()}
          </tr>
        </thead>
        <tbody>
          {this.buildRows()}
        </tbody>
      </table>
    );
  }
}

export default ReportTable;
