define(["js/views/baseview", "jquery", "underscore", "gettext",
        "js/models/assignment_grade", "js/views/feedback_notification",
        "js/models/subsection_lab", "jquery.cookie"],

        function(BaseView, $, _, gettext, AssignmentGrade, NotificationView, SubsectionLab) {
    var l10nNotGraded = gettext('Not Graded');
    var OverviewAssignmentGrader = BaseView.extend({
        // instantiate w/ { graders : CourseGraderCollection, el : <the gradable-status div> }
        events : {
            "click .menu-toggle" : "showGradeMenu",
            "click .menu li" : "selectGradeType"
        },
        initialize : function() {
            // call template w/ {assignmentType : formatname, graders : CourseGraderCollection instance }
            this.template = _.template(
                    // TODO move to a template file
                    '<h4 class="status-label"><%= assignmentType %></h4>' +
                    '<a data-tooltip="Mark/unmark this subsection as graded" class="menu-toggle" href="#">' +
                        '<% if (!hideSymbol) {%><i class="icon fa fa-check"></i><%};%>' +
                    '</a>' +
                    '<ul class="menu">' +
                        '<% graders.each(function(option) { %>' +
                            '<li><a <% if (option.get("type") == assignmentType) {%>class="is-selected" <%}%> href="#"><%= option.get("type") %></a></li>' +
                        '<% }) %>' +
                        '<li><a class="gradable-status-notgraded" href="#">' +
                        l10nNotGraded +
                        '</a></li>' +
                    '</ul>');
            this.assignmentGrade = new AssignmentGrade({
                locator : this.$el.closest('.id-holder').data('locator'),
                graderType : this.$el.data('initial-status')});
            // TODO throw exception if graders is null
            this.graders = this.options['graders'];
            var cachethis = this;
            // defining here to get closure around this
            this.removeMenu = function(e) {
                e.preventDefault();
                cachethis.$el.removeClass('is-active');
                $(document).off('click', cachethis.removeMenu);
            };
            this.hideSymbol = this.options['hideSymbol'];
            this.render();

            this.labsterLabs = this.options['labsterLabs'];
            this.labSelectionEl = this.options['labSelectionEl'];
            if (this.labSelectionEl) {
                this.labSelectionMenuEl = this.labSelectionEl.find('.gradable-status');
                var labId = this.labSelectionEl.data('lab-id');
                if (this.$el.find('.status-label').text().toUpperCase() == 'LAB' && labId) {
                    var selectedLab = this.labsterLabs.find(function(lab) {
                        return parseInt(lab.get('id')) == parseInt(labId);
                    });

                    if (selectedLab) {
                        this.labSelectionMenuEl.find('.status-label').text(selectedLab.get('name'));
                    }
                    this.labSelectionEl.show();
                }
            }
        },
        render : function() {
            var graderType = this.assignmentGrade.get('graderType');
            this.$el.html(this.template(
                {
                    assignmentType : (graderType == 'notgraded') ? l10nNotGraded : graderType,
                    graders : this.graders,
                    hideSymbol : this.hideSymbol
                }
            ));
            if (this.assignmentGrade.has('graderType') && this.assignmentGrade.get('graderType') != "notgraded") {
                this.$el.addClass('is-set');
            }
            else {
                this.$el.removeClass('is-set');
            }
        },
        showGradeMenu : function(e) {
            e.preventDefault();
            // I sure hope this doesn't break anything but it's needed to keep the removeMenu from activating
            e.stopPropagation();
            // nasty global event trap :-(
            $(document).on('click', this.removeMenu);
            this.$el.addClass('is-active');
        },
        renderLabSelection : function() {
            var template = _.template(
                    // TODO move to a template file
                    '<h4 class="status-label"></h4>' +
                    '<a data-tooltip="Select lab" class="menu-toggle" href="#">' +
                    '</a>' +
                    '<form id="duplicate-lab-form" action="/labster/duplicate-lab/" method="post">' +
                    '<input type="hidden" name="csrfmiddlewaretoken">' +
                    '<input type="hidden" name="parent_locator">' +
                    '<input type="hidden" name="source_locator">' +
                    '<input type="hidden" name="redirect_url">' +
                    '</form>' +
                    '<ul class="menu">' +
                        '<% labs.each(function(lab) { %>' +
                            '<li><a href="#" data-lab-id="<%= lab.get("id") %>" data-location="<%= lab.get("template_location") %>"><%= lab.get("name") %></a></li>' +
                        '<% }) %>' +
                    '</ul>');

            this.labSelectionMenuEl.empty().append(template({labs: this.labsterLabs}));
            this.labSelectionEl.show();

            var cachethis = this;
            this.labSelectionEl.find('li a').click(function(ev) {
                var linkEl = $(ev.target);
                var labId = linkEl.data('lab-id');
                var statusLabel = cachethis.labSelectionEl.find('.status-label');

                statusLabel.empty().append(linkEl.text());
                statusLabel.after('<div class="due-date-input"><a class="save-lab" href="#">save lab</a></div>');

                cachethis.labSelectionEl.find('ul').hide();

                cachethis.labSelectionEl.find('a.save-lab').click(function(ev) {

                    cachethis.subsectionLab = new SubsectionLab({
                        locator : cachethis.$el.closest('.id-holder').data('locator'),
                        labId: parseInt(labId)});

                    cachethis.subsectionLab.save('labId', parseInt(labId), {success: function() {
                        // POST to duplicate content
                        var form = $('#duplicate-lab-form');
                        var csrftoken = $.cookie('csrftoken');
                        var parent_location = linkEl.closest('.unit-settings').data('locator');
                        var source_location = linkEl.data('location');
                        var redirect_url = window.location.href;

                        form.find('input[name=parent_locator]').val(parent_location);
                        form.find('input[name=source_locator]').val(source_location);
                        form.find('input[name=redirect_url]').val(redirect_url);
                        form.find('input[name=csrfmiddlewaretoken]').val(csrftoken);
                        form.submit();
                    }});

                    $(ev.target).remove();
                    cachethis.labSelectionEl.find('.menu-toggle').unbind('click');
                });
            });

            this.labSelectionEl.find('.menu-toggle').click(function(ev) {
                cachethis.labSelectionEl.find('ul').show();
            });
        },
        selectGradeType : function(e) {
              e.preventDefault();

              this.removeMenu(e);

                  var saving = new NotificationView.Mini({
                      title: gettext('Saving')
                  });
                  saving.show();

              // TODO I'm not happy with this string fetch via the html for what should be an id. I'd rather use the id attr
              // of the CourseGradingPolicy model or null for notgraded (NOTE, change template's if check for is-selected accordingly)
              this.assignmentGrade.save(
                      'graderType',
                      ($(e.target).hasClass('gradable-status-notgraded')) ? 'notgraded' : $(e.target).text(),
                      {success: function () { saving.hide(); }}
                  );

              if ($(e.target).text() == 'Lab') {
                  // show the lab selection popup
                  this.renderLabSelection();

              } else {
                  this.labSelectionEl.hide();
                  this.labSelectionMenuEl.empty();
              }

              this.render();
        }
    });
    return OverviewAssignmentGrader;
});
