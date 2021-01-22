import Input from '.input';
import Results from '.results';


export default Form = (props) => {
    return (
        <div className="top-hits-search__input">
          <div className="top-hits-search__input-field">
            <form action="/search/">
              <Input input={props.input} onChange={props.handleInputChange} />
            </form>
            <Results input={props.input} results={props.results} />
          </div>
        </div>
    );
};
