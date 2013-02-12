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
        },

        events: {
            "click #signin": "signin"
        },

        signin:function (event) {
            event.preventDefault(); // Don't let this button submit the form
            $('.alert-error').hide(); // Hide any errors on a new submit

            var request_params = {}; // could be site name
            navigator.id.request(request_params);

            console.log('Logging in... ');

            navigator.id.watch({
                loggedInUser: 'hitz@stanford.edu',
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
                                console.log(["Login request details: ", data]);

                                if(data.error) {  // If there is an error, show the error messages
                                    $('.alert-error').text(data.error.text).show();
                                }
                                else { // If not, send them back to the home page
                                    window.location.replace('/');
                                }
                            },
                            error: function(xhr, status, err) {
                                alert("Login failure: "+err+" ("+status+")");
                            }
                        });
                    }
                },
                onlogout: function() {
                    $.ajax({
                        url: '/logout',
                        type: 'POST',
                        data: { came_from: "/" },
                        success: function () { window.location.reload(); },
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

    // below is just a reminder to implement this somewhere.
    $('#signout').click(function() { navigator.id.logout(); return false;});

    return exports;
});
