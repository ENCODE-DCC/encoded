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
        this._links = attrs._links || {};
        delete attrs._links;
        this.links = {};
        _.each(this._links, _.bind(function (value, rel) {
          if (rel == 'self') {
            // pass
          } else if (_.isArray(value)) {
            this.links[rel] = _.map(value, _.bind(function (value) {
              var new_obj = new this.constructor();
              new_obj.url = value.href;
              return new_obj;
            }, this));
          } else {
            var new_obj = new this.constructor();
            new_obj.url = value.href;
            this.links[rel] = new_obj;
          }
        }, this));
        this._embedded = attrs._embedded || {};
        delete attrs._embedded;
        return attrs;
      },

      url: function() {
        return this._links.self ? this._links.self.href : Model.__super__.url.call(this);
      },

      isNew: function() {
        return this._links.self ? true : Model.__super__.isNew.call(this);
      }
    });

    Collection = Backbone.Collection.extend({

      constructor: function (obj, options) {
        Collection.__super__.constructor.call(this, this.parse(_.clone(obj)), options);
      },

      parse: function(obj) {
        var items;
        if (!obj) obj = {};
        this._links = obj._links || {};
        delete obj._links;
        this._embedded = obj._embedded || {};
        delete obj._embedded;
        this.attributes = obj;
        if (this.itemRel !== undefined) {
          items = this._embedded[this.itemRel];
        } else {
          items = this._embedded.items;
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
        return this._links.self ? this._links.self.href : Collection.__super__.url.call(this);
      }

    });

    return {
      Model: Model,
      Collection: Collection
    };

}));
