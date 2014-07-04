define(["backbone", "underscore"], function(Backbone, _) {
    var SubsectionLab = Backbone.Model.extend({
        defaults : {
            labId: null,
            locator : null // locator for the block
        },
        idAttribute: 'locator',
        urlRoot : '/xblock/',
        url: function() {
            // add ?fields=labId to the request url (only needed for fetch, but innocuous for others)
            return Backbone.Model.prototype.url.apply(this) + '?' + $.param({fields: 'labId'});
        }
    });
    return SubsectionLab;
});
