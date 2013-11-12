'use strict';

    // http://www.ianbicking.org/blog/2013/04/new-considered-harmful.html
    var class_ = function (superclass, properties) {
        var prototype;
        if (! properties) {
            // We're creating an object with no superclass
            prototype = superclass;
        } else {
            prototype = Object.create(superclass.prototype);
            for (var a in properties) {
                if (properties.hasOwnProperty(a)) {
                    prototype[a] = properties[a];
                }
            }
        }
        var ClassObject = function () {
            var newObject = Object.create(prototype);
            if (newObject.constructor) {
                newObject.constructor.apply(newObject, arguments);
            }
            return newObject;
        };
        ClassObject.prototype = prototype;
        return ClassObject;
    };

module.exports = class_;
