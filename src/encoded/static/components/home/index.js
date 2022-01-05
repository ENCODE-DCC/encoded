// node_modules
import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
// libs
import { svgIcon } from '../../libs/svg-icons';
// libs/ui
import { Modal, ModalHeader, ModalBody } from '../../libs/ui/modal';
// components
import { isLight, tintColor } from '../datacolors';
import * as globals from '../globals';
// local
import {
    CARDS_FOR_MAIN,
    CARDS_FOR_COLLECTIONS,
    CARDS_FOR_OTHER_DATA,
    CARDS_FOR_DOCUMENTATION,
} from './card_definitions';
import { CARD_GAP_WIDTH } from './constants';
import SearchSection from './search';


/**
 * Displays the trigger for the help modal.
 */
const CardHelp = ({ card, onHelpClick }) => (
    <div className="card-help">
        <button
            type="button"
            name={`card-help-${card.id}`}
            onClick={onHelpClick}
            className="card-help__trigger"
            aria-label={`Open description of ${card.title}`}
        >
            {svgIcon('questionCircle')}
        </button>
    </div>
);

CardHelp.propTypes = {
    /** Card to display help for */
    card: PropTypes.shape({
        id: PropTypes.string,
        title: PropTypes.string,
    }).isRequired,
    /** Called when the user clicks the help trigger button */
    onHelpClick: PropTypes.func.isRequired,
};


/**
 * Displays a count of the number of search results for the currently rendering card.
 */
const SearchCount = ({ count }) => (
    <div className="card-count">
        {count}
    </div>
);

SearchCount.propTypes = {
    /** Number of results for this card */
    count: PropTypes.number.isRequired,
};


/**
 * Displays a single card.
 */
const Card = ({ card, sectionId, columns, format, searchCount, searchedTerm, onHelpClick }) => {
    // Calculate the number of pixels to subtract from the column size to fit the row exactly. Add a
    // couple pixels to the result to adjust for errors in some browser.
    const columnFactor = (CARD_GAP_WIDTH * (columns - 1)) / columns + 2;

    /**
     * Called when the user clicks the help trigger button.
     */
    const onCardHelpClick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        onHelpClick(card);
    };

    return (
        <a
            href={`${card.link}${card.useSearchTerm && searchedTerm ? `&searchTerm=${searchedTerm}` : ''}`}
            className={`card card--${sectionId}-${card.id} ${format}${searchCount > 0 ? ' card--highlighted' : ''}`}
            style={{
                backgroundColor: card.color,
                borderColor: tintColor(card.color, -0.5),
                color: isLight(card.color) ? '#000' : '#fff',
                flexBasis: `calc(${100 / columns}% - ${columnFactor}px)`,
            }}
        >
            <div className="card__icon">{card.icon}</div>
            <div className="card__title">{card.title}</div>
            {card.help && <CardHelp card={card} onHelpClick={onCardHelpClick} />}
            {card.displayCount && searchCount > 0 && <SearchCount count={searchCount} />}
        </a>
    );
};

Card.propTypes = {
    /** Card definition */
    card: PropTypes.object.isRequired,
    /** Card section ID from the card definitions object */
    sectionId: PropTypes.string.isRequired,
    /** Number of columns to display at non-mobile viewport widths */
    columns: PropTypes.number.isRequired,
    /** CSS class for the format of this card */
    format: PropTypes.string.isRequired,
    /** Number of results for this card's collections; positive integer highlights card */
    searchCount: PropTypes.number.isRequired,
    /** Searched term that resulted in the searched collection titles */
    searchedTerm: PropTypes.string.isRequired,
    /** Called when the user clicks the help icon */
    onHelpClick: PropTypes.func.isRequired,
};


/**
 * Display the cards for one section of the home page.
 */
const CardSection = ({ cardDefinitions, searchedCollectionTitles, searchedTerm, onHelpClick }) => (
    <section className="home-section">
        {cardDefinitions.cards.map((card) => {
            // Cards with associated collections overlapping the collections from the user-entered
            // search term get highlighted. Extract the matching collection titles and add up all
            // their counts to display in the card.
            const matchingCollectionTitles = _.intersection(card.collections, Object.keys(searchedCollectionTitles));
            const matchingCollectionsCount = matchingCollectionTitles.reduce((count, collectionTitle) => (
                count + searchedCollectionTitles[collectionTitle]
            ), 0);
            return (
                <Card
                    key={card.id}
                    sectionId={cardDefinitions.id}
                    card={card}
                    columns={cardDefinitions.columns}
                    format={cardDefinitions.format}
                    searchCount={matchingCollectionsCount}
                    searchedTerm={searchedTerm}
                    onHelpClick={onHelpClick}
                />
            );
        })}
    </section>
);

CardSection.propTypes = {
    /** Definitions of cards in this section */
    cardDefinitions: PropTypes.object.isRequired,
    /** Titles of collections matching search term */
    searchedCollectionTitles: PropTypes.object.isRequired,
    /** Searched term that resulted in the searched collection titles */
    searchedTerm: PropTypes.string.isRequired,
    /** Called when the user clicks the help icon */
    onHelpClick: PropTypes.func.isRequired,
};


/**
 * Unconditionally displays a modal containing a card's help text.
 */
const CardHelpModal = ({ card, onClose }) => (
    <Modal closeModal={onClose} labelId="card-help-modal" descriptionId="card-help-description" widthClass="sm">
        <ModalHeader title={card.title} labelId="card-help-modal" closeModal={onClose} />
        <ModalBody>
            <div id="card-help-description" role="document">
                {card.help}
            </div>
        </ModalBody>
    </Modal>
);

CardHelpModal.propTypes = {
    /** Card whose help text gets displayed in the modal */
    card: PropTypes.shape({
        title: PropTypes.string,
        help: PropTypes.string,
    }).isRequired,
    /** Called when the user requests closing the modal */
    onClose: PropTypes.func.isRequired,
};


/**
 * Renders the entire home page.
 */
const Home = ({ context }) => {
    const itemClass = globals.itemClass(context, 'view-item');
    /** Collection titles and counts relevant to user-entered search term */
    const [collectionTitles, setCollectionTitles] = React.useState({});
    /** The searched term that resulted in the collection titles */
    const [searchedTerm, setSearchedTerm] = React.useState('');
    /** ID of card currently displaying help */
    const [helpCard, setHelpCard] = React.useState(null);

    /**
     * Called when the user-entered search term receives relevant collection titles.
     * @param {array} receivedCollectionTitles - List of collection titles relevant to search term
     */
    const onReceiveCollectionTitles = (receivedCollectionTitles, searchTerm) => {
        setCollectionTitles(receivedCollectionTitles);
        setSearchedTerm(searchTerm);
    };

    /**
     * Called when the user clicks the help icon of the given card. Triggers the display of the
     * corresponding help modal.
     * @param {object} card Card whose help icon was clicked
     */
    const onHelpClick = (card) => {
        setHelpCard(card);
    };

    return (
        <div className={itemClass}>
            <SearchSection onReceiveCollectionTitles={onReceiveCollectionTitles} />
            <CardSection
                cardDefinitions={CARDS_FOR_MAIN}
                searchedCollectionTitles={collectionTitles}
                searchedTerm={searchedTerm}
                onHelpClick={onHelpClick}
            />
            <CardSection
                cardDefinitions={CARDS_FOR_COLLECTIONS}
                searchedCollectionTitles={collectionTitles}
                searchedTerm={searchedTerm}
                onHelpClick={onHelpClick}
            />
            <CardSection
                cardDefinitions={CARDS_FOR_OTHER_DATA}
                searchedCollectionTitles={collectionTitles}
                searchedTerm={searchedTerm}
                onHelpClick={onHelpClick}
            />
            <CardSection
                cardDefinitions={CARDS_FOR_DOCUMENTATION}
                searchedCollectionTitles={collectionTitles}
                searchedTerm={searchedTerm}
                onHelpClick={onHelpClick}
            />
            {helpCard && <CardHelpModal card={helpCard} onClose={() => setHelpCard(null)} />}
        </div>
    );
};

Home.propTypes = {
    /** Home page static data */
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(Home, 'Portal');
