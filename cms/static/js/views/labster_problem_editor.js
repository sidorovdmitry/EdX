define(["jquery", "underscore", "gettext", "codemirror", "js/views/feedback_notification", "js/views/baseview",
        "js/views/metadata", "js/collections/metadata", "jquery.inputnumber"],
    function ($, _, gettext, CodeMirror, NotificationView, BaseView, MetadataView, MetadataCollection) {

        var LabsterProblemEditor = BaseView.extend({

            initialize: function() {
                BaseView.prototype.initialize.call(this);
                this.element = $(".xblock-editor");

                this.multipleChoiceTemplate = "( ) incorrect\n( ) incorrect\n(x) correct\n";
                this.checkboxChoiceTemplate = "[x] correct\n[ ] incorrect\n[x] correct\n";
                this.stringInputTemplate = "= answer\n";
                this.numberInputTemplate = "= answer +- 0.001%\n";
                this.selectTemplate = "[[incorrect, (correct), incorrect]]\n";
                this.headerTemplate = "Header\n=====\n";
                this.explanationTemplate = "[explanation]\nShort explanation\n[explanation]\n";

            },

            events: {
                "click .format-buttons a": "onToolbarButton"
            },

            render: function() {
                this.initializeEditors();
                return this;
            },

            initializeEditors: function() {
                var textarea = this.element.find("textarea")[0];
                this.codeMirror = CodeMirror.fromTextArea(textarea, {
                    mode: "application/json", 
                    lineNumbers: false, 
                    lineWrapping: false});

                if (this.problem) {
                    this.codeMirror.doc.setValue(this.problem.content_markdown);
                }
            },

            onToolbarButton: function(event) {
                event.preventDefault();
                var el = $(event.currentTarget);
                var selection = this.codeMirror.getSelection();
                var new_selection = null;
                switch (el.attr('class')) {
                    case "multiple-choice-button":
                        new_selection = this.insertMultipleChoice(selection);
                        break;
                    case "string-button":
                        new_selection = this.insertStringInput(selection);
                        break;
                    // case "number-button":
                    //     new_selection = this.insertNumberInput(selection);
                    //     break;
                    // case "checks-button":
                    //     new_selection = this.insertCheckboxChoice(selection);
                    //     break;
                    // case "dropdown-button":
                    //     new_selection = this.insertSelect(selection);
                    //     break;
                    case "header-button":
                        new_selection = this.insertHeader(selection);
                        break;
                    case "explanation-button":
                        new_selection = this.insertExplanation(selection);
                        break;
                }

                if (new_selection !== null) {
                    this.codeMirror.replaceSelection(new_selection);
                    return this.codeMirror.focus();
                }
            },

            insertGenericChoice: function(selectedText, choiceStart, choiceEnd, template) {
                var cleanSelectedText, line, lines, revisedLines, _i, _len;
                if (selectedText.length > 0) {
                    cleanSelectedText = selectedText.replace(/\n+/g, '\n').replace(/\n$/, '');
                    lines = cleanSelectedText.split('\n');
                    revisedLines = '';
                    for (_i = 0, _len = lines.length; _i < _len; _i++) {
                        line = lines[_i];
                        revisedLines += choiceStart;
                        if (/^\s*x\s+(\S)/i.test(line)) {
                            line = line.replace(/^\s*x\s+(\S)/i, '$1');
                            revisedLines += 'x';
                        } else {
                            revisedLines += ' ';
                        }
                        revisedLines += choiceEnd + ' ' + line + '\n';
                    }
                    return revisedLines;
                } else {
                    return template;
                }
            },

            insertGenericInput: function(selectedText, lineStart, lineEnd, template) {
                if (selectedText.length > 0) {
                    return lineStart + selectedText + lineEnd;
                } else {
                    return template;
                }
            },

            insertMultipleChoice: function(selectedText) {
                return this.insertGenericChoice(selectedText, '(', ')', this.multipleChoiceTemplate);
            },

            insertCheckboxChoice: function(selectedText) {
                return this.insertGenericChoice(selectedText, '[', ']', this.checkboxChoiceTemplate);
            },

            insertStringInput: function(selectedText) {
                return this.insertGenericInput(selectedText, '= ', '', this.stringInputTemplate);
            },

            insertNumberInput: function(selectedText) {
                return this.insertGenericInput(selectedText, '= ', '', this.numberInputTemplate);
            },

            insertSelect: function(selectedText) {
                return this.insertGenericInput(selectedText, '[[', ']]', this.selectTemplate);
            },

            insertHeader: function(selectedText) {
                return this.insertGenericInput(selectedText, '', '\n====\n', this.headerTemplate);
            },

            insertExplanation: function(selectedText) {
                return this.insertGenericInput(selectedText, '[explanation]\n', '\n[explanation]', this.explanationTemplate);
            },

            save: function(http_method, callback) {
                var content_markdown = this.codeMirror.doc.getValue();
                this.problem.content_markdown = content_markdown;

                $.ajax({
                    type: http_method,
                    url: this.problem_url,
                    contentType: "application/json",
                    dataType: "json",
                    data: JSON.stringify(this.problem),
                    success: function(response) {
                        if (callback) {
                            callback(response);
                        }
                    }
                });
            }

        });

        return LabsterProblemEditor;
    }
);
