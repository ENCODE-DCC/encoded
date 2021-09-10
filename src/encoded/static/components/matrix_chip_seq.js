import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';
import NavBarMultiSearch from './top_hits/multi/search';
import Tooltip from '../libs/ui/tooltip';

const newPageData = [
    {
        id: '1',
        order: 0,
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
        order: 1,
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
        order: 2,
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
        order: 3,
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
        order: 4,
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
        order: 5,
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
        order: 6,
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
        order: 7,
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
        order: 8,
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
        order: 9,
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
        order: 10,
        header: {
            text: 'Matrix11',
            url: 'http://www.google.com',
        },
        url: 'search/?type=Experiment&control_type!=*&status=released&perturbed=false',
        content: 'Lorem ipsum11',
        footer: 'Lorem ipsum footer',
    },
];

const Card = ({ item, index }) => {
    const clearHighlightedCard = (element) => {
        const children = element?.children || [];

        for (let i = 0; i < children.length; i += 1) {
            const child = children[i];
            child.classList.remove('home-page-card--highlighted');
        }
    };

    const onMouseEnterCard = (e) => {
        const element = e.currentTarget;

        clearHighlightedCard(element.parentElement);
        element.classList.add('home-page-card--highlighted');
    };

    const onMouseLeaveCard = (e) => {
        const element = e.currentTarget;

        clearHighlightedCard(element.parentElement);
        element.classList.remove('home-page-card--highlighted');
    };

    return (
        <div className={`home-page-card ${index === 0 ? 'is-ref' : ''} ${index !== -1 ? 'carousel-seat' : ''}`} style={{ order: index }} onMouseEnter={(e) => onMouseEnterCard(e)} onMouseLeave={(e) => onMouseLeaveCard(e)}>
            <div className="home-page-card__header"><a href={item.header.url}>{item.header.text}</a></div>
            <div className="home-page-card__content">{item.content}</div>
            <div className="home-page-card__footer">{item.footer}</div>
        </div>
    );
};

Card.propTypes = {
    item: PropTypes.object.isRequired,
    index: PropTypes.number,
};

Card.defaultProps = {
    index: -1,
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

const Carousel = () => {
    const [expanded, setExpanded] = React.useState(true);
    const [cards, setCards] = React.useState([...newPageData]);
    const carouselFullView = React.useRef(null);
    const carouselDataLength = newPageData.length;
    const [transformTranslateX, setTransformTranslateX] = React.useState(16);
    let isReversed = false;

    const setLayout = () => {
        setExpanded(!expanded);
    };

    const openedCards = cards.map((item, index) => <Card key={item.id} item={item} index={index} />);

    const next = (el) => {
        const seats = document.querySelectorAll('.carousel-seat');
        if (el.nextElementSibling) {
            return el.nextElementSibling;
        }
        isReversed = false;
        return seats[0];
    };

    const prev = (el) => {
        const seats = document.querySelectorAll('.carousel-seat');
        if (el.previousElementSibling) {
            return el.previousElementSibling;
        }
        isReversed = true;
        return seats[seats.length - 1];
    };

    const moveCard = (e, direction) => {
        const el = document.querySelector('.is-ref');
        el?.classList?.remove('is-ref');

        const carousel = carouselFullView.current;

        let i;
        let j;
        let newSeat;
        let ref;

        if (direction === 1) {
            newSeat = next(el);
            carousel.classList.remove('is-reversing');
        } else {
            newSeat = prev(el);
            carousel.classList.add('is-reversing');
        }
        newSeat.classList.add('is-ref');
        newSeat.style.order = 1;
        const seats = document.querySelectorAll('.carousel-seat');

        for (i = j = 2, ref = seats.length; (ref >= 2 ? j <= ref : j >= ref); i = ref >= 2 ? ++j : --j) {
            newSeat = next(newSeat);
            newSeat.style.order = i;
        }
        carousel.classList.remove('is-set');
        return setTimeout((() => {
            carousel.classList.add('is-set');
            const cardsWidth = carousel.offsetWidth;
            const cardWidth = seats[0]?.offsetWidth || 180;
            setTransformTranslateX(Math.floor(isReversed ? 1 : -1 * (100 / (cardsWidth / cardWidth))));
        }), 50);
    };

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
                <div className="home-page-full-view__arrow" onClick={(e) => moveCard(e, -1)} role="button" tabIndex={-1} onKeyPress={() => {}}>
                    <i className="facet-chevron icon icon-chevron-left" />
                </div>
                <div className="home-page-full-view__region">
                    <div ref={carouselFullView} className="home-page-full-view__region__carousel carousel is-set" style={{ transform: `translateX(${transformTranslateX})` }}>
                        { openedCards }
                    </div>
                </div>
                <div className="home-page-full-view__arrow" onClick={(e) => moveCard(e, 1)} role="button" tabIndex={-1} onKeyPress={() => {}}>
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
                <img className="home-page-layout__brand--brand-img" src="/static/img/home_image.svg" alt="text" />
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
                                <input type="search" placeholder="Search..." onKeyUp={(e) => searchBoxKeyUp(e)} />
                                <button type="button">
                                    <i className="icon icon-search" />
                                </button>
                            </div>
                            <input ref={clear} type="button" value="Clear search" className="home-page-layout__search__search-region__clear" placeholder="clear" text="Clear Search" onClick={() => resetSearch()} />
                        </fieldset>
                    </form>
                </div>
            </div>
            <div className="home-page-layout__carousel">
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
