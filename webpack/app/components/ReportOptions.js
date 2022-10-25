import React from 'react';
import ReactDOM from 'react-dom';

class ReportOptions extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidUpdate() {
    let controls = [];
    let form = $(ReactDOM.findDOMNode(this));
    if (form.length > 0) {

      // Bind change event to input fields
      controls = form.context.getElementsByTagName("input");
      for (let [index, node] of Object.entries(controls)) {
        node.addEventListener("change", this.props.onChange);
      }

      // Bind change event to textarea fields
      controls = form.context.getElementsByTagName("textarea");
      for (let [index, node] of Object.entries(controls)) {
        node.addEventListener("change", this.props.onChange);
      }

      // Bind change event to select fields
      controls = form.context.getElementsByTagName("select");
      for (let [index, node] of Object.entries(controls)) {
        node.addEventListener("change", this.props.onChange);
      }
    }
  }

  render() {
    if (!this.props.controls) {
      return null;
    }
    return (
      <div name={this.props.name} className={this.props.className}
            dangerouslySetInnerHTML={{__html: this.props.controls}}>
      </div>
    );
  }
}

export default ReportOptions;
