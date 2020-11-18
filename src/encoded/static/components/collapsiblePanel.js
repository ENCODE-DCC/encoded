import React from 'react';
import { Panel, PanelBody, PanelHeading } from '../libs/ui/panel';
import PropTypes from 'prop-types';

class CollapsiblePanel extends React.Component {
  constructor(props) {
      super(props);
      this.showBody = false;
      this.title = this.props.title;
      this.panelId = this.props.panelId;
      this.headId = this.panelId + "Heading";
      this.bodyId = this.panelId + "Body";
      this.handleClick = this.handleClick.bind(this);
      this.handleHover = this.handleHover.bind(this);
      this.handleLeave = this.handleLeave.bind(this);
      this.styles = {diplay: 'clock'};
      this.symbolStyles = {
        fontWeight: "bold",
        float: "right",
        marginLeft: "5px"
      };

  }

  handleHover() {
    let heading = document.getElementById(this.headId).parentElement;
    heading.style.cursor = "pointer";
    heading.style.backgroundColor = "#777";
  }


  handleLeave() {
      let heading = document.getElementById(this.headId).parentElement;
      heading.style.cursor = "default";
      heading.style.backgroundColor = "#d8d8d8";
  }

  handleClick(e) {
    let body = document.getElementById(this.bodyId);
    let symbol = e.currentTarget.getElementsByTagName("span")[1]
    if(symbol.innerHTML === "+") {
      symbol.innerHTML = "-";
    }else {
      symbol.innerHTML = "+";
    }
    if (body.style.display === "none") {
      body.style.display = "block";
    } else {
      body.style.display = "none";
    }

  }
  render() {

    return (
      <Panel>
          <PanelHeading >
            <div id={this.headId} >
              <h4 onClick = {this.handleClick} onMouseOver={this.handleHover} onMouseLeave={this.handleLeave}>
                <span >{this.title}</span>
                <span style={this.symbolStyles}>-</span>
              </h4>
            </div>
          </PanelHeading>
          <PanelBody style={this.styles}>
              <div id={this.bodyId} style={this.styles}>
                {this.props.content}
              </div>
          </PanelBody>
      </Panel>
    )
  }
}

CollapsiblePanel.propTypes = {
  title: PropTypes.string,
  content: PropTypes.object,
  panelId: PropTypes.string,
};

export default CollapsiblePanel;
