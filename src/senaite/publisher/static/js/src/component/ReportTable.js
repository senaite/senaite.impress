import React from 'react';
import moment from 'moment';
import ReportRow from "./ReportRow.js";
import CCContacts from "./CCContacts.js";


class ReportTable extends React.Component {

  constructor(props) {
    super(props);
    this.api = props.api;

    this.state = {
      columns: [
        {
          name: "title",
          title: "Title",
          formatter: this.formatTitleColumn.bind(this)
        },
        {
          name: "ContactFullName",
          title: "Contact",
          formatter: this.formatContactColumn.bind(this)
        },
        {
          name: "CCContact",
          title: "CC Contacts",
          formatter: this.formatCCContactColumn.bind(this)
        },
        {
          name: "CCEmails",
          title: "CC Emails",
          formatter: this.formatEmailColumn.bind(this)
        },
        {
          name: "ClientTitle",
          title: "Client"
        },
        {
          name: "DateReceived",
          title: "Date Received",
          formatter: this.formatDateColumn.bind(this)
        }
      ]
    };
  }

  formatContactColumn(column, model) {
    let value = model[column.name];
    let email = model.ContactEmail;
    let el = value;
    if (email) {
      el = <a href="mailto:{email}">{value}</a>;
    }
    return el;
  }

  formatCCContactColumn(column, model) {
    return <CCContacts api={this.api} model={model} />;
  }

  formatDateColumn(column, model) {
    let value = model[column.name];
    return moment(value).startOf('day').fromNow();
  }

  formatEmailColumn(column, model) {
    let value = model[column.name];
    return <a href="mailto:{value}">{value}</a>;
  }

  formatTitleColumn(column, model) {
    let value = model[column.name];
    let url = model.absolute_url;
    return `<a href="${url}">${value}</a>`;
  }

  buildHeader() {
    let header = [];
    let columns = this.state.columns;
    columns.map(
      column =>
        header.push(
          <th key={column.name}>{column.title}</th>
        ));
    return header;
  }

  buildRows() {
    let rows = [];
    let uids = this.props.uids;
    uids.map(
      uid =>
        rows.push(
          <ReportRow uid={uid} columns={this.state.columns} api={this.api} key={uid} />
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
