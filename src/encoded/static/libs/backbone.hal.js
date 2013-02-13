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
    var Collection, Model, exports = {};

    Model = exports.Model = Backbone.Model.extend({

      constructor: function (attrs, options) {
        if (options.url) this.url = options.url;
        if (!attrs && exports.resource_cache) {
          attrs = exports.resource_cache[options.url];
        }
        Model.__super__.constructor.call(this, this.parse(_.clone(attrs)), options);
      },

      parse: function(attrs) {
        if (!attrs) attrs = {};
        this._links = attrs._links || {};
        delete attrs._links;
        this._embedded = attrs._embedded || {};
        delete attrs._embedded;
        this.makeLinks();
        return attrs;
      },

      makeLinks: function() {
        this.links = {};
        if (this._embedded.resources) {
          exports.resource_cache = this._embedded.resources;
        }
        _.each(this._links, _.bind(function (value, rel) {
          if (rel == 'self') {
            // pass
          } else if (_.isArray(value)) {
            this.links[rel] = _.map(value, _.bind(function (list_value) {
              return new this.constructor(null, {url: list_value.href});
            }, this));
          } else {
            this.links[rel] = new this.constructor(null, {url: value.href});
          }
        }, this));
      },

      url: function() {
        return this._links.self ? this._links.self.href : Model.__super__.url.call(this);
      },

      isNew: function() {
        return this._links.self ? true : Model.__super__.isNew.call(this);
      }
    });

    Collection = exports.Collection = Backbone.Collection.extend({

      itemRel: 'items',

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
        exports.resource_cache = this._embedded.resources;
        return _.map(this._links[this.itemRel], function(item) {
          return exports.resource_cache[item.href];
        });
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

    return exports;

}));
