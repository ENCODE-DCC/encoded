import React, {component} from 'react'

class Table extends Component{

    constructor(props){

        super(props)
        this.state={
           germlineGenes: []
        }
    }

    render (){

        return (
            <div>
                <h1>germline Table</h1>

            </div>
        
        )
        
        }
}

renderTableData(data){
const data =this.props.data;
console.log(data);
console.log(data.map(i=>{return i.significance}));
console.log(data.map(i=>{return i.significance==='Positiive'}));
console.log(data.map(i=>{return i.significance==='Positive and Variant'}));
console.log(data.map(i=>{return i.significance==='Variant'}));

    return this.state.germlineGenes =  data.map(i =>{return i.significance==' Positive' or i.significance=='Positive and Variant' or i.significance==='Variant'});
}


export default germlineChart;
