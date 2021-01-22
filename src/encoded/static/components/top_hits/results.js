import {
    Title,
    Item
} from './links';


const makeTitle = (result) => {
    return `${result.key} (${result.count})`;
};


export const Items = (props) => {
    return (
        <ul>
          {
              props.items.map(
                  item => (
                      <Item
                        key={item["@id"]}
                        item={item}
                        href={item["@id"]}
                      />
                  )
              )
          }
        </ul>
    );
};


export const Section = (props) => {
    return (
        <>
          <Title value={props.title} href={props.href}/>
          <Items
            items={props.items}
          />
        </>
    );
};


export default Results = (props) => {
    return (
        <div className='top-hits-search__suggested-results'>
          {
              props.results.map(
                  (result) => (
                      <Section
                        key={result.key}
                        title={makeTitle(result)}
                        href={`/search/?type=${result.key}&searchTerm=${props.input}`}
                        items={result.hits}
                      />
                  )
            )}
        </div>
    );
};
