import React from 'react';
import PropTypes from 'prop-types';
import { FetchedData, Param } from '../fetched';
import globals from '../globals';
import { ResultTable } from '../search';


function openLinksInNewWindow(e) {
    if (e.isDefaultPrevented()) return;

    // intercept links and open in new tab
    let target = e.target;
    while (target && (target.tagName.toLowerCase() !== 'a')) {
        target = target.parentElement;
    }
    if (!target) return;

    e.preventDefault();
    window.open(target.getAttribute('href'), '_blank');
}


class SearchBlockEdit extends React.Component {
    componentDidMount() {
        // focus the first "Select" button in the search results
        const button = this.domNode.querySelector('button.btn-primary');
        if (button) {
            button.focus();
        }
    }

    render() {
        const styles = { maxHeight: 300, overflow: 'scroll', clear: 'both' };
        return (
            <div
                className="well" style={styles} onClick={openLinksInNewWindow}
                ref={(comp) => { this.domNode = comp; }}
            >
                <ResultTable {...this.props} mode="picker" />
            </div>
        );
    }
}


export const ItemPreview = (props) => {
    const context = props.data;
    if (context === undefined) return null;
    const Listing = globals.listing_views.lookup(context);
    return (
        <ul className="nav result-table" onClick={openLinksInNewWindow}>
            <Listing context={context} key={context['@id']} />
        </ul>
    );
};

ItemPreview.propTypes = {
    data: PropTypes.object,
};

ItemPreview.defaultProps = {
    data: undefined,
};


export class ObjectPicker extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = {
            browsing: false,
            search: '',
            searchInput: '',
        };

        // Bind this to non-React methods.
        this.handleInput = this.handleInput.bind(this);
        this.handleSearch = this.handleSearch.bind(this);
        this.handleBrowse = this.handleBrowse.bind(this);
        this.handleFilter = this.handleFilter.bind(this);
        this.handleSelect = this.handleSelect.bind(this);
        this.handleClear = this.handleClear.bind(this);
    }

    componentDidUpdate(prevProps, prevState) {
        if (!this.props.value && !this.state.searchInput && this.state.searchInput !== prevState.searchInput) {
            this.input.focus();
        } else if (this.props.value !== prevProps.value) {
            this.clear.focus();
        }
    }

    handleInput(e) {
        if (e.keyCode === 13) {
            e.preventDefault();
            this.handleSearch();
        }
        this.setState({ searchInput: e.target.value });
    }

    handleSearch() {
        this.setState({ search: this.state.searchInput, browsing: true });
    }

    handleBrowse(e) {
        e.preventDefault();
        this.setState({ browsing: !this.state.browsing });
    }

    handleFilter(href) {
        this.setState({ searchParams: href });
    }

    handleSelect(e) {
        const value = e.currentTarget.id;
        this.setState({ browsing: false, searchInput: '', search: '' });
        this.props.onChange(value);
    }

    handleClear(e) {
        this.props.onChange(null);
        this.setState({ browsing: false, searchInput: '', search: '', searchParams: null });
        e.preventDefault();
    }

    render() {
        const url = this.props.value;
        const previewUrl = url;
        const actions = [
            <button key={1} className="btn btn-primary" onClick={this.handleSelect}>Select</button>,
        ];
        let searchParams = this.state.searchParams || this.props.searchBase;
        if (this.state.search) {
            searchParams += `&searchTerm=${globals.encodedURIComponent(this.state.search)}`;
        }
        return (
            <div className={`item-picker${this.props.disabled ? ' disabled' : ''}`}>
                <div className="item-picker-preview" style={{ display: 'inline-block', width: 'calc(100% - 120px)' }}>
                    {url ?
                        <FetchedData>
                            <Param name="data" url={previewUrl} />
                            <ItemPreview {...this.props} />
                        </FetchedData>
                    : ''}
                    {!url ?
                        <input
                            value={this.state.searchInput}
                            ref={(input) => { this.input = input; }}
                            type="text"
                            placeholder="Enter a search term (accession, uuid, alias, ...)"
                            onChange={this.handleInput}
                            onBlur={this.handleSearch}
                            onKeyDown={this.handleInput}
                            disabled={this.props.disabled}
                        />
                    : ''}
                    {this.state.error ? <div className="alert alert-danger">{this.state.error}</div> : ''}
                </div>
                {!this.props.disabled &&
                    <div className="pull-right">
                        <button className="clear-button" ref={(button) => { this.clear = button; }} onClick={this.handleClear}><i className="icon icon-times" /></button>
                        {' '}<button className={`btn btn-primary${this.state.browsing ? ' active' : ''}`} onClick={this.handleBrowse}>Browse&hellip;</button>
                    </div>
                }
                {this.state.browsing ?
                    <FetchedData>
                        <Param name="context" url={`/search/${searchParams}`} />
                        <SearchBlockEdit
                            searchBase={searchParams}
                            restrictions={this.props.restrictions}
                            hideTextFilter={!url}
                            actions={actions}
                            onChange={this.handleFilter}
                        />
                    </FetchedData>
                : ''}
            </div>
        );
    }
}

ObjectPicker.propTypes = {
    onChange: PropTypes.func,
    restrictions: PropTypes.object,
    searchBase: PropTypes.string,
    value: PropTypes.string,
    disabled: PropTypes.bool,
};

ObjectPicker.defaultProps = {
    restrictions: {},
    searchBase: '?mode=picker',
    disabled: false,
};
