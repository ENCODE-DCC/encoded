// Support for async loading, adapted from https://github.com/umdjs/umd
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['backbone', 'underscore'], function (Backbone, _) {
      return (root.HAL = factory(Backbone, _));
    });
  } else {
    root.HAL = factory(Backbone, _);
  }
}(this, function(Backbone, _) {
    var Collection, Model;

    Model = Backbone.Model.extend({

      constructor: function (attrs, options) {
        Model.__super__.constructor.call(this, this.parse(_.clone(attrs)), options);
      },

      parse: function(attrs) {
        if (!attrs) attrs = {};
        this.links = attrs._links || {};
        delete attrs._links;
        this.embedded = attrs._embedded || {};
        delete attrs._embedded;
        return attrs;
      },

      url: function() {
        return this.links.self ? this.links.self.href : Model.__super__.url.call(this);
      },

      isNew: function() {
        return !(this.links.self);
      }
    });

    Collection = Backbone.Collection.extend({

      constructor: function (obj, options) {
        Collection.__super__.constructor.call(this, this.parse(_.clone(obj)), options);
      },

      parse: function(obj) {
        var items;
        if (!obj) obj = {};
        this.links = obj._links || {};
        delete obj._links;
        this.embedded = obj._embedded || {};
        delete obj._embedded;
        this.attributes = obj;
        if (this.itemRel !== undefined) {
          items = this.embedded[this.itemRel];
        } else {
          items = this.embedded.items;
        }
        return items;
      },

      reset: function(obj, options) {
        if (!options) options = {};
        // skip parsing if obj is an Array (i.e. reset items only)
        if (!_.isArray(obj)) {
          obj = this.parse(_.clone(obj));
        }
        options.parse = false;
        return Collection.__super__.reset.call(this, obj, options);
      },

      url: function() {
        return this.links.self ? this.links.self.href : Collection.__super__.url.call(this);
      }

    });

    return {
      Model: Model,
      Collection: Collection
    };

}));
