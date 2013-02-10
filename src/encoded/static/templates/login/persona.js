$(function() {

    var currentUser = {user};

    navigator.id.watch({
        loggedInUser: currentUser,
        onlogin: function(assertion) {
            if (assertion) {
                var $form = $("<form method=POST "+
                    "      action='{login}'>" +
                    "  <input type='hidden' " +
                    "         name='assertion' " +
                    "         value='" + assertion + "' />" +
                    "  <input type='hidden' " +
                    "         name='came_from' "+
                    "         value='{came_from}' />" +
                    "  <input type='hidden' " +
                    "         name='csrf_token' "+
                    "         value='{csrf_token}' />" +
                    "</form>").appendTo($("body"));
                $form.submit();
            }
        },
        onlogout: function() {
            var $form = $("<form method=POST "+
                "      action='{logout}'>" +
                "  <input type='hidden' " +
                "         name='came_from' "+
                "         value='{came_from}' />" +
                "  <input type='hidden' " +
                "         name='csrf_token' "+
                "         value='{csrf_token}' />" +
                "</form>").appendTo($("body"));
            $form.submit();
        }
    });
});