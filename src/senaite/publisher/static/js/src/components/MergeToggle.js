import React from 'react';


class MergeToggle extends React.Component {
  /** Toggle for merging reports
   */

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <input type="checkbox"
             value={this.props.value}
             onChange={this.props.onChange}
             name={this.props.name}
             className={this.props.className}/>
    );
  }
}

export default MergeToggle;
