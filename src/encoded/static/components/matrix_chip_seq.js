import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';
import NavBarMultiSearch from './top_hits/multi/search';
import Tooltip from '../libs/ui/tooltip';

const EXPANDED_CARD_SIZE = 4;

const newPageData = [
    {
        id: '1',
        header: {
            text: 'Encylopedia1',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum1',
        footer: 'Lorem ipsum footer',
    },
    {
        id: '2',
        header: {
            text: 'Encylopedia2',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum2',
        footer: 'Lorem ipsum footer',
    },
    {
        id: '3',
        header: {
            text: 'Encylopedia3',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum3',
        footer: 'Lorem ipsum footer',
    },
    {
        id: '4',
        header: {
            text: 'Encylopedia4',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum4',
        footer: 'Lorem ipsum footer',
    },
    {
        id: '5',
        header: {
            text: 'Single cell5',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum5',
        footer: 'Lorem ipsum footer',
    },
    {
        id: '6',
        header: {
            text: 'FCC6',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum6',
        footer: 'Lorem ipsum footer',
    },
    {
        id: '7',
        header: {
            text: 'Reference Epigenome7',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum7',
        footer: 'Lorem ipsum footer',
    },
    {
        id: '8',
        header: {
            text: 'Experiments8',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum8',
        footer: 'Lorem ipsum footer',
    },
    {
        id: '9',
        header: {
            text: 'Annotation9',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum9',
        footer: 'Lorem ipsum footer',
    },
    {
        id: '10',
        header: {
            text: 'Biosample10',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum10',
        footer: 'Lorem ipsum footer',
    },
    {
        id: '11',
        header: {
            text: 'Matrix11',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum11',
        footer: 'Lorem ipsum footer',
    },
];

const Card = ({ item }) => (
    <div className="home-page-card">
        <div className="home-page-card__header"><a href={item.header.url}>{item.header.text}</a></div>
        <div className="home-page-card__content">{item.content}</div>
        <div className="home-page-card__footer">{item.footer}</div>
    </div>
);

Card.propTypes = {
    item: PropTypes.object.isRequired,
};

const ClosedPlate = ({ item }) => (
    <div className="home-page-closed-card">
        <div className="home-page-closed-card__content">
            <div className="home-page-closed-card__content--text">
                <a href={item.url}>{item.content}</a>
            </div>
        </div>
    </div>
);

ClosedPlate.propTypes = {
    item: PropTypes.object.isRequired,
};

const MobileDisplayControl = (props) => (
    props.expanded
    ?
        <div className="home-page-layout-control__expanded" onClick={props.setLayout} role="button" tabIndex={-1} onKeyPress={() => {}}>
            <div className="home-page-layout-control__expanded__first-item" />
            <div className="home-page-layout-control__expanded__second-item" />
            <div className="home-page-layout-control__expanded__third-item" />
        </div>
    :
        <div className="home-page-layout-control__collapsed" onClick={props.setLayout} role="button" tabIndex={-1} onKeyPress={() => {}}>
            <div>
                <div className="home-page-layout-control__collapsed__item" />
                <div className="home-page-layout-control__collapsed__item" />
            </div>
            <div>
                <div className="home-page-layout-control__collapsed__item" />
                <div className="home-page-layout-control__collapsed__item" />
            </div>
        </div>
);

MobileDisplayControl.propTypes = {
    expanded: PropTypes.bool.isRequired,
    setLayout: PropTypes.func.isRequired,
};


const getCardIndice = (data) => {
    const closedCard1Start = 0;
    let closedCard1End = 0;
    let openCardStart = 0;
    let openCardEnd = 0;
    let closedCard2Start = 0;
    let closedCard2End = 0;
    const dataCount = data.length;

    if (dataCount <= EXPANDED_CARD_SIZE) {
        openCardEnd = EXPANDED_CARD_SIZE;
    } else if (dataCount === EXPANDED_CARD_SIZE + 1) {
        closedCard1End = 1;
        openCardStart = closedCard1End + 1;
        openCardEnd = EXPANDED_CARD_SIZE;
    } else {
        const closedCardCount = dataCount - EXPANDED_CARD_SIZE;
        const firstClosedCardRegionCount = Math.floor(closedCardCount / 2);

        closedCard1End = firstClosedCardRegionCount;
        openCardStart = closedCard1End;
        openCardEnd = closedCard1End + EXPANDED_CARD_SIZE;
        closedCard2Start = openCardEnd;
        closedCard2End = dataCount;
    }

    return {
        closedCard1Start,
        closedCard1End,
        openCardStart,
        openCardEnd,
        closedCard2Start,
        closedCard2End,
    };
};

const Carousel = () => {
    const [expanded, setExpanded] = React.useState(true);
    const [cards, setCards] = React.useState([...newPageData]);
    const {
        closedCard1Start,
        closedCard1End,
        openCardStart,
        openCardEnd,
        closedCard2Start,
        closedCard2End,
    } = getCardIndice(cards);
    let closedCards1;
    let openedCards;
    let closedCards2;

    const setLayout = () => {
        setExpanded(!expanded);
    };

    const shift = (direction) => {
        const arr = [...cards];

        if (direction === 1) {
            const firstItem = arr.shift();
            arr.push(firstItem);

            setCards(arr);
            return;
        }

        const lastItem = arr.pop();
        setCards([lastItem, ...arr]);
    };

    if (closedCard1End !== 0) {
        closedCards1 = cards.slice(closedCard1Start, closedCard1End).map((item) => <ClosedPlate key={item.id} item={item} />);
    }

    if (openCardEnd !== 0) {
        openedCards = cards.slice(openCardStart, openCardEnd).map((item) => <Card key={item.id} item={item} />);
    }

    if (closedCard2Start !== 0) {
        closedCards2 = cards.slice(closedCard2Start, closedCard2End).map((item) => <ClosedPlate key={item.id} item={item} />);
    }

    return (
        <>
            <div className="home-page-mobile-view">
                <div>
                    <MobileDisplayControl expanded={expanded} setLayout={setLayout} />
                </div>
                <div className="home-page-mobile-card-view">
                    <div className={`${expanded ? 'home-page-cards-mobile-expanded' : 'home-page-cards-mobile-collapsed'}`}>
                        {
                            cards.map((item) => <Card key={item.id} item={item} />)
                        }
                    </div>
                </div>
            </div>
            <div className="home-page-full-view">
                <div className="home-page-full-view__arrow" onClick={() => shift(1)} role="button" tabIndex={-1} onKeyPress={() => {}}>
                    <i className="facet-chevron icon icon-chevron-left" />
                </div>
                <div className="home-page-full-view__region">
                    <div className="home-page-full-view__region__carousel">
                        { closedCards1 }
                        { openedCards }
                        { closedCards2 }
                    </div>
                </div>
                <div className="home-page-full-view__arrow" onClick={() => shift(-1)} role="button" tabIndex={-1} onKeyPress={() => {}}>
                    <i className="facet-chevron icon icon-chevron-right" />
                </div>
            </div>
        </>
    );
};

/**
 * Container for ChIP-Seq Matrix page.
 *
 * @param {context}  context - Context object
 * @returns
 */
const ChIPSeqMatrix = ({ context }) => {
    const i = 0;
    console.log(i);
    const clear = React.useRef(null);
    const form = React.useRef(null);

    const resetSearch = () => {
        form.current.reset();
        clear.current.style.display = 'none';
    };

    const searchBoxKeyUp = (e) => {
        const { target } = e;

        clear.current.style.display = target.value.trim() === '' ? 'none' : 'inline';
        console.error(target.value);
    };

    return (
        <div className="home-page-layout">
            <div className="home-page-layout__brand">
                <img className="home-page-layout__brand--brand-img" src="https://test.encodedcc.org/static/img/classic-image-5290.jpg" alt="text" />
            </div>
            <div className="home-page-layout__search">
                <div className="home-page-layout__search__search-region">
                    <form ref={form} action="/search/">
                        <fieldset>
                            <legend className="sr-only">Encode search</legend>
                            <div className="home-page-layout__search__search-region__text-region">
                                <div className="label--inline">Search ENCODE portal</div>
                                <Tooltip
                                    trigger={<i className="icon icon-question-circle icon-3x" />}
                                    tooltipId="search-encode"
                                    css="tooltip-home-info"
                                >
                                    Search the entire ENCODE portal by using terms like &ldquo;skin,&rdquo; &ldquo;ChIP-seq,&rdquo; or &ldquo;CTCF.&rdquo;
                                </Tooltip>
                            </div>
                            <div className="home-page-layout__search__search-region__search">
                                <input type="search" placeholder="Search.." onKeyUp={(e) => searchBoxKeyUp(e)} />
                                <button type="button">
                                    <i className="icon icon-search" />
                                </button>
                            </div>
                            <input ref={clear} type="button" value="Clear search" className="home-page-layout__search__search-region__clear" placeholder="clear" text="Clear Search" onClick={() => resetSearch()} />
                        </fieldset>
                    </form>
                </div>
            </div>
            <div className="home-page-layout__caurosel">
                <div>
                    <Carousel />
                </div>
            </div>
        </div>
    );
};

ChIPSeqMatrix.propTypes = {
    context: PropTypes.object.isRequired,
};

ChIPSeqMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};

globals.contentViews.register(ChIPSeqMatrix, 'ChipSeqMatrix');
