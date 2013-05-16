define(['exports', 'jquery', 'underscore', 'navigator', 'app', 'base',
    'text!templates/navbar.html'],
function navbar(exports, $, _, navigator, app, base, navbar_template) {

    // The top navbar
    var NavBar = exports.NavBarView = base.View.extend({
        template: _.template(navbar_template),

        initialize: function () {
            // TODO: re-renders more than necessary, should split into subviews.
            console.log("Initializing navbar");
            this.listenTo(app.router, 'all', this.on_route);
        },

        // Preprocess the global_sections adding an active class to the current section
        global_sections: function global_sections() {
            var view = this;
            return _(this.model.global_sections).map(function (action) {
                return _.extend(action, {
                    'class': view.current_route === action.id ? 'active': ''
                });
            });
        },

        user_actions: function user_actions() {
            return this.model.user_actions;
        },

        events: {
            "click #signin": "signin",
            "click #signout": "signout"
        },

        on_route: function(event) {
            var route_parts = event.split(':');
            // Only render on the main route not the overlay route.
            if (route_parts[0] !== 'route') return;
            this.current_route = route_parts[1];
            this.render();
            NavBar.toggle_login();
        },

        signout: function(event) {
            event.preventDefault();
            console.log('Logging out (persona)');
            navigator.id.logout();
        },

        signin:function (event) {
            event.preventDefault(); // Don't let this button submit the form
            $('.alert-error').hide(); // Hide any errors on a new submit

            var request_params = {}; // could be site name
            console.log('Logging in (persona) ');
            navigator.id.request(request_params);


            navigator.id.watch({
                loggedInUser: app.user.email,
                onlogin: function(assertion) {
                    if (assertion) {
                        $.ajax({
                            url:'/login',
                            type:'POST',
                            dataType:"json",
                            data: JSON.stringify({
                                "assertion": assertion,
                                "came_from": "/"
                            }),
                            contentType: 'application/json',
                            headers: { "X-Genuine-Request": "Bonafide ENCODE3 Submission"},
                            success:function (data) {
                                console.log("Login request headers: "+data["headers"]);
                                console.log("Login info:");
                                console.log(data["info"]);

                                if(data.error) {
                                     $('.alert-error').text(data.error.text).show();
                                }
                                else if (data.status != 'okay') {
                                    $('.alert-error').text('This seems impossible, but Persona returned your status as something other than ok').show();
                                }
                                else { // If not, send them back to the home page
                                    $('.alert-error').hide();
                                    app.user.email = data.email;
                                    //_each(app.Config.user_actions(), function(action) {
                                    //    action = action._extend({'class': hide});
                                    //});
                                    NavBar.toggle_login();
                                    // possibly this should trigger on navbar view directly
                                    //Backbone.history.navigate(location.href, {trigger: true, replace: true});
                                }
                            },
                            error: function(xhr, status, err) {
                                    var msg = "";
                                     // If there is an error, show the error messages
                                    msg = "Login Failure.  Access is restricted to ENCODE consortium members.  <a href='mailto:encode-help@lists.stanford.edu'>Request an account</a>";
                                    $('.alert-error').text(msg).show();
                                    console.log("Persona error: "+err+" ("+status+")");
                            }
                        });
                    }
                },
                onlogout: function() {
                    console.log("Persona thinks we need to log out");
                    $.ajax({
                        url: '/logout',
                        type: 'POST',
                        data: JSON.stringify({ came_from: "/" }),
                        success: function () {
                            console.log('reloading after persona logout');
                            app.user = { email: undefined };
                            app.router.trigger('logout');
                            NavBar.toggle_login();
                            //Backbone.history.navigate(location.href, {trigger: true, replace: true});
                            //window.location.reload();
                        },
                       error: function(xhr, status, err) {
                            alert("Logout failure: "+err+" ("+status+")");
                        }
                    });
                }
            });
        }
    },
    {
        slot_name: 'navbar',

        toggle_login: function toggleLogin() {
            if (app.user.email) {
                $("#signout").text("Log out: "+app.user.email);
                $("#signout").parent().show();
                $("#signin").parent().hide();
            } else {
                $("#signin").parent().show();
                $("#signout").parent().hide();
            }
        }

    });


    return exports;
});
