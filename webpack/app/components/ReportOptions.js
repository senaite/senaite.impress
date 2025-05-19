import React, { useRef } from 'react';
import ReactDOM from 'react-dom';

class ReportOptions extends React.Component {
  constructor(props) {
    super(props);
    this.containerRef = null;
  }

  componentDidUpdate() {
    if (!this.containerRef) return;

    const formNode = this.containerRef;
    const tags = ['input', 'textarea', 'select'];

    tags.forEach(tag => {
      const controls = formNode.getElementsByTagName(tag);
      Array.from(controls).forEach(node => {
        node.removeEventListener('change', this.props.onChange); // Avoid duplicates
        node.addEventListener('change', this.props.onChange);
      });
    });
  }

  render() {
    if (!this.props.controls) return null;

    return (
      <div
        ref={(ref) => { this.containerRef = ref; }}
        name={this.props.name}
        className={this.props.className}
        dangerouslySetInnerHTML={{ __html: this.props.controls }}
      />
    );
  }
}

export default ReportOptions;
