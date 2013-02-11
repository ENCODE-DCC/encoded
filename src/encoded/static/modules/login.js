// brazenly ripped from pyramid_persona templates/persona.js then wrapped in require
define(['exports', 'jquery', 'underscore', 'base', 'navigator', 'assert'],
function login(exports, $, _, base, navigator, assert) {

    exports.LoginView = base.View.extend({
        initialize:function () {
            console.log('Initializing Login View');
        },

        //render: function () {
            // shouldn't render anything
         //   console.log("render nothing!");
         //   return this;
        //},
        events: {
            "click #signin": "signin"
        },

        signin:function (event) {
            event.preventDefault(); // Don't let this button submit the form
            $('.alert-error').hide(); // Hide any errors on a new submit

            var request_params = {}; // could be site name
            navigator.id.request(request_params);

            console.log('Loggin in... ');
            var formValues = {
                assertion: this.model.assertion,
                came_from: this.model.came_from
            };

            navigator.id.watch({
                loggedInUser: this.model.user,
                onlogin: function(formValues) {
                    if (formValues['assertion']) {
                        $.ajax({
                            url:url,
                            type:'POST',
                            dataType:"json",
                            data: formValues,
                            headers: { "X-Genuine-Request": "Bonafide ENCODE3 Submission"},
                            success:function (data) {
                                console.log(["Login request details: ", data]);

                                if(data.error) {  // If there is an error, show the error messages
                                    $('.alert-error').text(data.error.text).show();
                                }
                                else { // If not, send them back to the home page
                                    window.location.replace('/');
                                }
                            }
                        });
                    }
                }
            });
        }
    },
    {
        route_name: 'login'
    });

    return exports;

});