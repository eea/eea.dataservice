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

SelectAutocompleteWidget = function(context){
    var self = this;

    self.available_choices_box = null;
    self.clear_filter_btn = null;
    self.filter_box = null;
    self.filter = null;
    self.info_x = null;
    self.info_y = null;
    self.info = null;
    self.widget = null;

    self.select = context.get(0);

    self.filter_box = null;
    self.build_widget();

    self.options = _make_values(self.select);
    jQuery(self.select).css('display','none');
    self.set_select_values(self.available_choices_box, self.options);

    // jQuery(self.filter).css('display','none');
    // jQuery(self.info).css('display','none');

    var preselected = self.get_selected_option(self.select);
    self.set_selection(self.available_choices_box, preselected);

    self.refresh_info();

    jQuery(self.filter_box).bind('keyup', function(e){
        jQuery(self.info).css('display','block');
        var filtered = self.filter_values(self.options, this.value);
        self.set_select_values(self.available_choices_box, filtered);
        self.refresh_info();
        self.commit_to_form();
        return true;
    });

    jQuery(self.clear_filter_btn).bind('click', function(e){
        self.filter_box.value = "";
        var selected_option = self.get_selected_option(self.available_choices_box);
        self.set_select_values(self.available_choices_box, self.options);
        self.set_selection(self.available_choices_box, selected_option);
        self.refresh_info();
        self.commit_to_form();
        // jQuery(self.info).css('display','none');
        return true;
    });

    jQuery(self.available_choices_box).bind('change', function(e){
        self.commit_to_form();
    });

    // jQuery(self.widget).bind('mouseover', function(e){
    //     jQuery(self.filter).css('display','block');
    // });

    // jQuery(self.widget).bind('mouseout', function(e){
    //     jQuery(self.filter).css('display','none');
    //     // jQuery(self.info).css('display','none');
    // });
};

SelectAutocompleteWidget.prototype.build_widget = function(){
    var select = jQuery(this.select);
    var parent = select.parent();

    parent.append(jQuery(
        "<div style='width:650px; text-align:right' class='selectautocomplete_widget'>" +
        "<div class='info'>Showing <span class='x'>x</span> of <span class='y'>y</span>. Choose one.</div>" +
        "<select style='width:100%; text-align:left' class='available_choices' />" +
        "<div class='filter'>Filter: <input type='text' class='filter_box' style='width:300px' />&nbsp;" +
        "<input class='clear_filter' type='button' value='Clear' /></div>" +
        "</div>"
        ));

    this.filter_box = parent.find("input[class='filter_box']").get(0);
    this.clear_filter_btn = parent.find(".clear_filter").get(0);
    this.available_choices_box = parent.find(".available_choices").get(0);
    this.info_x = parent.find(".x").get(0);
    this.info_y = parent.find(".y").get(0);
    this.info = parent.find(".info").get(0);
    this.widget = parent.find(".selectautocomplete_widget").get(0);
    this.filter = parent.find(".filter").get(0);
};

SelectAutocompleteWidget.prototype.set_select_values = function(selectbox, values){
    this.clear_select_box(selectbox);
    jQuery(values).each(function(i, o){
        var label = _short(o.label);
        selectbox.options[i] = new Option(label, o.key, false, false ); //new Option(text, value, defaultSelected, selected)
    });
};

SelectAutocompleteWidget.prototype.set_selection = function(selectbox, value){
    if (value === null) {
        return;
    }

    for (var i=0; i<selectbox.options.length; i++ ) {
        var option = selectbox.options[i];
        if (option.value == value.key) {
            selectbox.selectedIndex = i;
            return;
        }
    }

    return null;
};

SelectAutocompleteWidget.prototype.commit_to_form = function(){
    var selected = this.get_selected_option(this.available_choices_box);
    this.set_selection(this.select, selected);
};

SelectAutocompleteWidget.prototype.clear_select_box = function(selectbox){
    selectbox.length = 0;
};

SelectAutocompleteWidget.prototype.get_selected_option = function(selectbox){
    var i = selectbox.selectedIndex;
    if (i == -1) {
        return null;
    }
    var option = selectbox.options[i];
    var o = {key:option.value, label:option.text};

    return o;
};

SelectAutocompleteWidget.prototype.filter_values = function(values, criteria){
    var res = [];
    jQuery(values).each(function(i, o) {
        if (o.label.toLowerCase().search(criteria.toLowerCase()) != -1) {
            res.push(o);
        }
    });
    return res;
};

SelectAutocompleteWidget.prototype.refresh_info = function(){
    jQuery(this.info_x).html(this.available_choices_box.length);
    jQuery(this.info_y).html(this.options.length);
};

jQuery.fn.SelectAutocompleteWidget = function(options){
    return this.each(function(){
        var context = jQuery(this);
        if(!context.data('SelectAutocompleteWidget')){
            var select = new SelectAutocompleteWidget(context);
            context.data('SelectAutocompleteWidget', select);
        }
    });
};

// vim: set ts=4 sw=4 et ai:
