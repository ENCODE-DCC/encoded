import * as globals from './globals';


const NewHomePage = () => {
    const i = 'test';

    return (
        <div>{i}</div>
    );
};

globals.contentViews.register(NewHomePage, 'new-home-page');
