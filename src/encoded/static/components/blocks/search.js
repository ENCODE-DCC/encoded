import React from 'react';
import PropTypes from 'prop-types';
import Table from '../collection';
import { FetchedData, Param } from '../fetched';
import * as globals from '../globals';
import { ResultTable, Listing } from '../search';


const SearchResultsLayout = (props) => {
    const context = props.context;
    const results = context['@graph'];
    const columns = context.columns;
    return (
        <div className="panel">
            <ul className="nav result-table">
                {results.length ?
                    results.map(result => Listing({ context: result, columns, key: result['@id'] }))
                : null}
            </ul>
        </div>
    );
};

SearchResultsLayout.propTypes = {
    context: PropTypes.object,
};

SearchResultsLayout.defaultProps = {
    context: null,
};


const SearchBlockEdit = (props) => {
    const styles = { maxHeight: 300, overflow: 'scroll' };
    return (
        <div className="well" style={styles}>
            <ResultTable {...props} context={props.data} mode="picker" />
        </div>
    );
};

SearchBlockEdit.propTypes = {
    data: PropTypes.object,
};

SearchBlockEdit.defaultProps = {
    data: null,
};

export default SearchBlockEdit;


class SearchBlock extends React.Component {
    shouldComponentUpdate(nextProps) {
        return (nextProps.value !== this.props.value);
    }

    render() {
        if (this.props.mode === 'edit') {
            let searchBase = this.props.value;
            if (!searchBase) searchBase = '?mode=picker';
            return (
                <FetchedData>
                    <Param name="data" url={`/search/${searchBase}`} />
                    <SearchBlockEdit searchBase={searchBase} onChange={this.props.onChange} />
                </FetchedData>
            );
        }

        const url = `/search/${this.props.value.search || ''}`;
        const Component = this.props.value.display === 'table' ? Table : SearchResultsLayout;
        return (
            <FetchedData>
                <Param name="context" url={url} />
                <Component href={url} />
            </FetchedData>
        );
    }
}

SearchBlock.propTypes = {
    value: PropTypes.any,
    mode: PropTypes.string,
    onChange: PropTypes.func,
};

SearchBlock.defaultProps = {
    value: '',
    mode: '',
    onChange: null,
};


const displayModeSelect = (
    <div><select>
      <option value="search">search results</option>
      <option value="table">table</option>
    </select></div>
);


globals.blocks.register({
    label: 'search block',
    icon: 'icon icon-search',
    schema: {
        type: 'object',
        properties: {
            display: {
                title: 'Display Layout',
                type: 'string',
                default: 'search',
                formInput: displayModeSelect,
            },
            search: {
                title: 'Search Criteria',
                type: 'string',
                formInput: <SearchBlock mode="edit" />,
            },
            className: {
                title: 'CSS Class',
                type: 'string',
            },
        },
    },
    view: SearchBlock,
}, 'searchblock');
