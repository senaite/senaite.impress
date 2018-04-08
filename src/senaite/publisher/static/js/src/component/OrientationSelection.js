import React from 'react';


class OrientationSelection extends React.Component {
  /** Selection for portrait/horizontal orientation
   */

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <select value={this.props.value}
              onChange={this.props.onChange}
              name={this.props.name}
              className={this.props.className}>
        <option key="portrait" value="portrait">Portrait</option>
        <option key="horizontal" value="horizontal">Horizontal</option>
      </select>
    );
  }
}

export default OrientationSelection;
