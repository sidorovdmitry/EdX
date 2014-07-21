define(["backbone", "js/models/settings/labster_lab"], function(Backbone, LabsterLab) {

var LabsterLabCollection = Backbone.Collection.extend({
    model : LabsterLab
});

return LabsterLabCollection;
}); // end define()
