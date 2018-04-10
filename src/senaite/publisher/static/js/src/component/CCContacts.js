import React from 'react';


class CCContacts extends React.Component {

  constructor(props) {
    super(props);
    this.api = props.api;
    this.state = {
      model: this.props.model,
      contacts: []
    };
  }

  fetch(uid) {
    let endpoint = `get/${uid}`;
    let contacts = this.state.contacts;
    this.api.get_json(endpoint).then(model => {
      contacts.push(model);
      this.setState(
        {contacts: contacts}
      );
    });
  }

  componentDidMount() {
    for(let contact of this.state.model.CCContact) {
      this.fetch(contact);
    }
  }

  buildElement() {
    let contacts = [];

    for (let contact of this.state.contacts) {
      let name = contact.Fullname;
      let el = <span>{name}</span>;
      let email = contact.EmailAddress;
      if (email) {
        el = <a href="mailto:{email}">{name}</a>;
      }
      contacts.push(
        <div key={contact.UID}>{el}</div>
      );
    }

    return contacts;
  }

  render() {
    if (!this.state.contacts.length) {
      return null;
    }
    return (
      this.buildElement()
    );
  }
}

export default CCContacts;
