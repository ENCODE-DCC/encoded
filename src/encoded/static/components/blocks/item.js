import React from 'react';
import PropTypes from 'prop-types';
import { FetchedData, Param } from '../fetched';
import * as globals from '../globals';
import { ObjectPicker } from '../inputs';


const ItemBlockView = (props) => {
    const ViewComponent = globals.contentViews.lookup(props.context);
    return <ViewComponent {...props} />;
};

export default ItemBlockView;


class FetchedItemBlockView extends React.Component {
    shouldComponentUpdate(nextProps) {
        return (nextProps.value.item !== this.props.value.item);
    }

    render() {
        const context = this.props.value.item;
        if (typeof context === 'object') {
            return <ItemBlockView context={context} />;
        }
        if (typeof context === 'string') {
            return (
                <FetchedData>
                    <Param name="context" url={context} />
                    <ItemBlockView />
                </FetchedData>
            );
        }
        return null;
    }
}

FetchedItemBlockView.propTypes = {
    value: PropTypes.object.isRequired,
};


globals.blocks.register({
    label: 'item block',
    icon: 'icon icon-paperclip',
    schema: {
        type: 'object',
        properties: {
            item: {
                title: 'Item',
                type: 'string',
                formInput: <ObjectPicker />
            },
            className: {
                title: 'CSS Class',
                type: 'string'
            }
        }
    },
    view: FetchedItemBlockView,
}, 'itemblock');
