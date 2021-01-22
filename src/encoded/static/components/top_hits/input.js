export default Input = (props) => {
    return (
        <input
          type="text"
          autoComplete="off"
          name="searchTerm"
          placeholder="Search for top hits by type"
          value={props.value}
          onChange={props.onChange}
        />
    );
};
