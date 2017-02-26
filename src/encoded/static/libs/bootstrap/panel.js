import React from 'react';


export class Panel extends React.Component {
    render() {
        const { addClasses, noDefaultClasses, ...other } = this.props;

        return (
            <div {...other} className={(noDefaultClasses ? '' : 'panel panel-default') + (addClasses ? ` ${addClasses}` : '')}>
                {this.props.children}
            </div>
        );
    }
}

Panel.propTypes = {
    addClasses: React.PropTypes.string, // Classes to add to outer panel div
    noDefaultClasses: React.PropTypes.bool, // T to not include default panel classes
    children: React.PropTypes.node,
};

Panel.defaultProps = {
    addClasses: '', // Classes to add to outer panel div
    noDefaultClasses: false, // T to not include default panel classes
    children: null,
};


export class PanelBody extends React.Component {
    render() {
        return (
            <div className={`panel-body${this.props.addClasses ? ` ${this.props.addClasses}` : ''}`}>
                {this.props.children}
            </div>
        );
    }
}

PanelBody.propTypes = {
    addClasses: React.PropTypes.string, // Classes to add to outer panel div
    children: React.PropTypes.node,
};

PanelBody.defaultProps = {
    addClasses: '',
    children: null,
};


export class PanelHeading extends React.Component {
    render() {
        return (
            <div className={`panel-heading${this.props.addClasses ? ` ${this.props.addClasses}` : ''}`}>
                {this.props.children}
            </div>
        );
    }
}

PanelHeading.propTypes = {
    addClasses: React.PropTypes.string, // Classes to add to outer panel div
    children: React.PropTypes.node,
};

PanelHeading.defaultProps = {
    addClasses: '',
    children: null,
};


export class PanelFooter extends React.Component {
    render() {
        return (
            <div className={`panel-footer${this.props.addClasses ? ` ${this.props.addClasses}` : ''}`}>
                {this.props.children}
            </div>
        );
    }
}

PanelFooter.propTypes = {
    addClasses: React.PropTypes.string, // Classes to add to outer panel div
    children: React.PropTypes.null,
};

PanelFooter.defaultProps = {
    addClasses: '',
    children: null,
};
