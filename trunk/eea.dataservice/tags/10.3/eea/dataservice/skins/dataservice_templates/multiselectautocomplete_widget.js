/*
* A near drop-in replacement of the MultiSelect lines widget from Plone.
* You still need to initialize the widget by pointing at the select element.
* You can use, for example make_multiselectautocomplete_widget($('select.multi_select_widget'))
* to quickly change all select widgets to MultiSelectAutocompleteWidget
*
* */

function _short(value) {
    var v = value.slice(0, 60);
    if (value.length > 57) {
        v += "...";
    }
    return v;
}

function _make_values(optionbox) {
    // Given a select HTML item, builds an array of objects with key,label
    var options = [];

    for (var i=0; i<optionbox.options.length; i++) {
        var o = {};
        o.key = optionbox.options[i].value;
        o.label = optionbox.options[i].text;
        options.push(o);
    }
    return options;
}

function _indexOf(arr, k){
    // returns the position of k in array arr, otherwise return -1
    var res = -1;
    jQuery(arr).each(function(i, v){
        if (v.key == k) {
            res = i;
            return false;
        }
    });
    return res;
}

function _combine(a1, a2) {
    // add two arrays: to a1, add the unique elements from a2

    jQuery(a2).each(function(i, v){
        if(_indexOf(a1, v.key) == -1){
            a1.push(v);
        }
    });
    return a1;
}

function _remove(a1, a2) {
    // remove stuff a1 from a2 and return result

    var res = [];
    jQuery(a2).each(function(i, v){
        if (_indexOf(a1, v.key) == -1){
            res.push(v);
        }
    });
    return res;
}

MultiSelectAutocompleteWidget = function(context){
    var self = this;
    // #5336 check if widget has already loded for the given context to avoid
    // table duplication
    if(jQuery(context).hasClass('loaded')) {
        return;
    }
    self.select = context.get(0);

    self.filter_box = null;   // the search input box
    self.available_choices_box = null;   // the available choices <select/>
    self.selected_choices_box = null;    // the selected choices <select/>
    self.move_left_btn = null;           // the move option to left button
    self.move_right_btn = null;          // the move option to right button
    self.clear_filter_btn = null;        // the clear filter search box button

    self.build_widget();

    self.options = _make_values(self.select);

    jQuery(self.select).css('display','none');
    self.set_select_values(self.available_choices_box, self.options);
    self.set_select_values(self.selected_choices_box,
                           self.get_selected_options(self.select));

    jQuery(self.available_choices_box).bind('click', function(e){
        self.selected_choices_box.selectedIndex = -1;
    });

    jQuery(self.selected_choices_box).bind('click', function(e){
        self.available_choices_box.selectedIndex = -1;
    });

    jQuery(self.filter_box).bind('keyup', function(e){
        var filtered = self.filter_values(self.options, this.value);
        self.set_select_values(self.available_choices_box, filtered);
        return true;
    });

    jQuery(self.move_right_btn).bind('click', function(e){
        var choice = self.get_selected_options(self.available_choices_box);
        var selected = _make_values(self.selected_choices_box);
        var combined = _combine(choice, selected);
        self.set_select_values(self.selected_choices_box, combined);
        self.commit_to_form();
        return true;
    });

    jQuery(self.move_left_btn).bind('click', function(e){
        var choice = self.get_selected_options(self.selected_choices_box);
        var selected = _make_values(self.selected_choices_box);
        var combined = _remove(choice, selected);
        self.set_select_values(self.selected_choices_box, combined);
        self.commit_to_form();
        return true;
    });

    jQuery(self.available_choices_box).bind('dblclick', function(e){
        jQuery(self.move_right_btn).trigger('click');
    });

    jQuery(self.selected_choices_box).bind('dblclick', function(e){
        jQuery(self.move_left_btn).trigger('click');
    });

    jQuery(self.clear_filter_btn).bind('click', function(e){
        self.filter_box.value = "";
        self.set_select_values(self.available_choices_box, self.options);
        return true;
    });
    jQuery(context).addClass('loaded');
};

MultiSelectAutocompleteWidget.prototype.commit_to_form = function(){
    this.set_select_values(this.select, _make_values(this.selected_choices_box));
    for (i=0; i<this.select.length; i++) {
        this.select.options[i].selected = true;
    }
};

MultiSelectAutocompleteWidget.prototype.get_selected_options = function(selectbox){
    var options = [];
    for (var i=0; i<selectbox.options.length; i++) {
        var option = selectbox.options[i];
        if (option.selected === true) {
            var o = {};
            o.key = option.value;
            o.label = option.text;
            options.push(o);
        }
    }
    return options;
};

MultiSelectAutocompleteWidget.prototype.clear_select_box = function(selectbox){
    selectbox.length = 0;
};

MultiSelectAutocompleteWidget.prototype.filter_values = function(values, criteria){
    var res = [];
    jQuery(values).each(function(i, o){
        if (o.label.toLowerCase().search(criteria.toLowerCase()) != -1) {
            res.push(o);
        }
    });
    return res;
};

MultiSelectAutocompleteWidget.prototype.set_select_values = function(selectbox, values){
    this.clear_select_box(selectbox);
    jQuery(values).each(function(i, o){
        var label = _short(o.label);
        selectbox.options[i] = new Option(label, o.key, false, false ); //new Option(text, value, defaultSelected, selected)
    });
};

MultiSelectAutocompleteWidget.prototype.build_widget = function(){
    // we need:
    // left available choices select box
    // right selected choices select box
    // the filter input text box and its clear button
    // move left & move right btn

    var select = jQuery(this.select);
    var parent = select.parent();
    parent.append(jQuery(
        "<table><tr>" +
        "<td valign='top' with='400'>Available choices: <br/>" +
        "<select multiple='multiple' style='width:450px; height:300px;' class='available_choices' /></td>" +
        "<td><input type='button' value='&rarr;' class='move_right' /><br/>" +
        "<input type='button' value='&larr;' class='move_left' /></td>" +
        "<td valign='top' width='300'>Selected choices: " +
        "<select class='selected_choices' multiple='multiple' style='width:100%;height:300px' /></td>" +
        "<tr><td>" +
        "Filter: <input type='text' class='filter_box' style='width:300px' /><input class='clear_filter' type='button' value='Clear' />" +
        "</td><td>&nbsp;</td><td>&nbsp;</td></tr>"
        ));

    this.filter_box = parent.find("input[class='filter_box']").get(0);
    this.move_left_btn = parent.find("input[class='move_left']").get(0);
    this.move_right_btn = parent.find("input[class='move_right']").get(0);
    this.available_choices_box = parent.find(".available_choices").get(0);
    this.selected_choices_box = parent.find(".selected_choices").get(0);
    this.clear_filter_btn = parent.find(".clear_filter").get(0);
};

function make_multiselectautocomplete_widget(elements) {
    // Use this function to quickly change all regular
    // multiselect widgets into versions that have autocomplete.
    // The elements should be a jQuery collection (selector result)
    // that points to the <select /> elements of the multiselect widget
    jQuery(elements).each(function(i, v){
        var widget = new MultiSelectAutocompleteWidget(el);
    });
}
