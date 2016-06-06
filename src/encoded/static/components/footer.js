'use strict';
var React = require('react');

var LoginFields = React.createClass({

	getInitialState: function() {
		return {username: '', password: ''};
	},
	handleUsernameChange: function(e) {
		this.setState({username: e.target.value});
	},
	handlePasswordChange: function(e) {
		this.setState({password: e.target.value});
	},
	handleSubmit: function(e) {
		e.preventDefault();
		var username = this.state.username.trim();
		var password = this.state.password.trim();
		if (!username || !password) {
			return;
		}
		this.props.onLogin({username: username, password: password});
		this.setState({username: '', password: ''});
	},
	render: function() {
		var clr = {'color':'black'};
		return ( 
				
				<div>
				<label>Username:</label>
				<input type="text" class="form-control" style={clr}
							 placeholder="fred.underwood"
							 onChange={this.handleUsernameChange}
							 value={this.state.username} />

				<label>Password</label>
				<input type="password" class="form-control" style={clr}
							 onChange={this.handlePasswordChange}
							 value={ this.state.password } />

				<button id="loginbtn" class="btn btn_primary" onClick={ this.handleSubmit }>Login</button>
				</div>
		);
	},
})		


var LoginForm = React.createClass({
	contextTypes: {
			fetch: React.PropTypes.func,
			session: React.PropTypes.object,
      navigate: React.PropTypes.func
	},

	loginToServer: function(data) {
			console.log(data);
			fetch('/login', {
				method: "POST",
				body: JSON.stringify(data),
				headers: {
					"Content-Type": "application/json",
				},
				credentials: "same-origin"
      })
      .then(response => {
        if (!response.ok) throw response;
        return response.json();
      })
      .then(session_properties => {
          console.log("got session props as", session_properties);
          this.context.session['auth.userid'] = data.username; 
          var next_url = window.location.href;
          if (window.location.hash == '#logged-out') {
              next_url = window.location.pathname + window.location.search;
          }
          this.context.navigate(next_url, {replace: true});
        },function(error) {
				console.log("we got an error during login", error);
      })
	},
	render: function() {
		return (
				<form>
				  <LoginFields onLogin={this.loginToServer} />
				</form>
		);
	},
});

var Footer = React.createClass({
    contextTypes: {
        session: React.PropTypes.object
    },

    propTypes: {
        version: React.PropTypes.string // App version number
    },

		//login form
		

    render: function() {
        var session = this.context.session;
        var disabled = !session;
        var userActionRender;

        if (!(session && session['auth.userid'])) {

            //userActionRender = <a href="#" data-trigger="login" disabled={disabled}>Submitter sign-in</a>;
						userActionRender = <LoginForm/>
        } else {
            userActionRender = <a href="#" data-trigger="logout">Submitter sign out</a>;
        }
        return (
            <footer id="page-footer">
                <div className="container">
                    <div className="row">
                        <div className="app-version">{this.props.version}</div>
                    </div>
                </div>
                <div className="page-footer">
                    <div className="container">
                        <div className="row">
                            <div className="col-sm-6 col-sm-push-6">
                                <ul className="footer-links">
                                    <li><a href="mailto:encode-help@lists.stanford.edu">Contact</a></li>
                                    <li><a href="http://www.stanford.edu/site/terms.html">Terms of Use</a></li>
                                    <li id="user-actions-footer">{userActionRender}</li>
                                </ul>
                                <p className="copy-notice">&copy;{new Date().getFullYear()} Stanford University.</p>
                            </div>

                            <div className="col-sm-6 col-sm-pull-6">
                                <ul className="footer-logos">
                                    <li><a href="/"><img src="/static/img/encode-logo-small-2x.png" alt="ENCODE" id="encode-logo" height="45px" width="78px" /></a></li>
                                    <li><a href="http://www.ucsc.edu"><img src="/static/img/ucsc-logo-white-alt-2x.png" alt="UC Santa Cruz" id="ucsc-logo" width="107px" height="42px" /></a></li>
                                    <li><a href="http://www.stanford.edu"><img src="/static/img/su-logo-white-2x.png" alt="Stanford University" id="su-logo" width="105px" height="49px" /></a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </footer>
        );
    }
});

module.exports = Footer;
