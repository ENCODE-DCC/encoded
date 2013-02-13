define(['exports', 'jquery', 'underscore', 'navigator', 'app', 'base',
    'text!templates/navbar.html'],
function navbar(exports, $, _, navigator, app, base, navbar_template) {

    // The top navbar
    exports.NavBarView = base.View.extend({
        template: _.template(navbar_template),

        initialize: function () {
            // TODO: re-renders more than necessary, should split into subviews.
            console.log("Initializeing navbar");
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

        on_route: function on_route(evt) {
            this.current_route = evt.substring(evt.indexOf(':')+1);
            this.render();
            if (app.user.email) {
                $("#signout").text("Log out: "+app.user.email);
                $("#signout").parent().show();
                $("#signin").parent().hide();
            } else {
                $("#signin").parent().show();
                $("#signout").parent().hide();
            }
        },

        events: {
            "click #signin": "signin",
            "click #signout": "signout"
        },

        signout: function(event) {
            event.preventDefault();
            console.log('Loggin out (persona)');
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
                            data: {
                                assertion: assertion,
                                came_from: "/"
                            },
                            headers: { "X-Genuine-Request": "Bonafide ENCODE3 Submission"},
                            success:function (data) {
                                console.log("Login request headers: "+data["headers"]);
                                console.log("Login info:");
                                console.log(data["info"]);

                                if(data.error) {  // If there is an error, show the error messages
                                    $('.alert-error').text(data.error.text).show();
                                }
                                else if (data.info.status != 'okay') {
                                    $('.alert-error').text('This seems impossible, but Persona returned your status as something other than ok').show();
                                }
                                else { // If not, send them back to the home page
                                    app.user.email = data.info.email;
                                    //_each(app.Config.user_actions(), function(action) {
                                    //    action = action._extend({'class': hide});
                                    //});
                                    app.router.trigger('login');
                                    // possibly this should trigger on navbar view directly
                                    //Backbone.history.navigate(location.href, {trigger: true, replace: true});
                                }
                            },
                            error: function(xhr, status, err) {
                                alert("Login failure: "+err+" ("+status+")");
                            }
                        });
                    }
                },
                onlogout: function() {
                    console.log("Persona thinks we need to log out");
                    $.ajax({
                        url: '/logout',
                        type: 'POST',
                        data: { came_from: "/" },
                        success: function () {
                            console.log('reloading after persona logout');
                            app.user = { email: undefined };
                            app.router.trigger('logout');
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
        slot_name: 'navbar'
    });


    return exports;
});
