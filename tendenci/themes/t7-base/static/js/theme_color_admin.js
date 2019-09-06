var cp1 = [
    ['#FFF8E3', '#CCCC9F', '#33332D', '#9FB4CC'],
    ['#DB4105', '#000000', '#FFFFFF']
]
var cp2 = [
    ['#10222B', '#95AB63', '#BDD684', '#E2F0D6'],
    ['#F6FFE0', '#000000', '#FFFFFF']
]
var cp3 = [
    ['#292929', '#5B7876', '#8F9E8B', '#F2E6B6'],
    ['#412A22', '#000000', '#FFFFFF']
]
var cp4 = [
    ['#595241', '#ACCFCC', '#8A0917', '#B8AE9C'],
    ['#000000', '#FFFFFF']
]
var cp5 = [
    ['#B9121B', '#4C1B1B', '#F6E497', '#FCFAE1'],
    ['#BD8D46', '#000000', '#FFFFFF']
]
var cp6 = [
    ['#CFC291', '#FFF6C5', '#A1E8D9', '#FF712C'],
    ['#695D46', '#000000', '#FFFFFF']
]
var cp7 = [
    ['#E7E8D1', '#D3CEAA', '#FBF7E4', '#424242'],
    ['#8E001C', '#000000', '#FFFFFF']
]
var cp8 = [
    ['#705B35', '#C7B07B', '#E8D9AC', '#FFF6D9'],
    ['#570026', '#000000', '#FFFFFF']
]
var cp9 = [
    ['#FCFFF5', '#D1DBBD', '#91AA9D', '#3E606F'],
    ['#193441', '#000000', '#FFFFFF']
]
var cp10 = [
    ['#105B63', '#FFFAD5', '#FFD34E', '#DB9E36'],
    ['#BD4932', '#000000', '#FFFFFF']
]

var themecolor = $('div.themecolor');
var colorInput = themecolor.find('input#colors');

function save_color_changes() {
    var data = {'csrfmiddlewaretoken':$('input[name="csrfmiddlewaretoken"]').val(),
                'colors':colorInput.val()
               };

    $.ajax({
        type: 'post',
        dataType: 'json',
        data: data,
        url: $('form#themecolorForm').attr('action')
    });
}

function apply_color_changes() {
    var input = colorInput.val();
    var color_dict = {};

    var values = input.split(';');
    for (var i=0; i<values.length; i++) {
        var value = values[i].split(':');
        if (typeof value[2] != 'undefined') {
            color_dict[value[0].trim()] = value[2].trim();
        }
    }
    less.modifyVars(color_dict);
    save_color_changes();
}

function update_color_changes(color) {
    var target = $(this).attr('target');
    var input = colorInput.val();
    var data = color.toHexString().toUpperCase();

    var values = input.split(';');
    for (var i=0; i<values.length; i++) {
        var value = values[i].split(':');
        if (value[0].trim() == target) {
            value[2] = data;
            values[i] = value.join(':');
        }
    }
    colorInput.val(values.join(';'));
    apply_color_changes();
}

function build_palettes(cp) {
    var colors = '';
    $("input.palette_admin").each(function(i) {
        var x = 0;
        var y = 0;
        var counter = i%7;
        if (counter > 3) {
            y = 1;
            x = counter%2;
        } else {
            y = 0;
            x = counter;
        }
        $(this).spectrum({
            preferredFormat: "hex6",
            color: cp[y][x],
            showPaletteOnly: true,
            showPalette: true,
            palette: cp,
            change: update_color_changes
        });
        colors += $(this).attr('target') + ':' + $(this).attr('label') + ':' + cp[y][x] + ';';
    });
    colorInput.val(colors);
    apply_color_changes();
}

function open_color_palette() {
    if(themecolor.hasClass('active')) {
        themecolor.removeClass('active');
    } else {
        themecolor.addClass('active');
    }
}

$('#admin-bar li#themecolor>a').on("click", function() {
    open_color_palette();
    return false;
});

themecolor.find('input[name="palette"]').on("change", function() {
    var paletteSelected = themecolor.find('input[name="palette"]:radio:checked');
    var value = paletteSelected.val();
    var cp = cp1;
    if (value === 'palette_1') { cp = cp1; }
    else if (value === '2') { cp = cp2; }
    else if (value === '3') { cp = cp3; }
    else if (value === '4') { cp = cp4; }
    else if (value === '5') { cp = cp5; }
    else if (value === '6') { cp = cp6; }
    else if (value === '7') { cp = cp7; }
    else if (value === '8') { cp = cp8; }
    else if (value === '9') { cp = cp9; }
    else if (value === '10') { cp = cp10; }
    build_palettes(cp);
});

themecolor.find('a.paletteSelector').on("click", function() {
    themecolor.find('div.colorSelector').slideUp('fast');
    themecolor.find('div.paletteSelector').slideDown('fast');
    return false;
});

themecolor.find('a.colorSelector').on("click", function() {
    var paletteSelected = themecolor.find('input[name="palette"]:radio:checked');
    var value = paletteSelected.val();
    if (value !== undefined) {
        themecolor.find('div.colorSelector').slideDown('fast');
        themecolor.find('div.paletteSelector').slideUp('fast');
    }
    return false;
});

themecolor.find('button#defaultBtn').on("click", function() {
    var paletteSelected = themecolor.find('input[name="palette"]:radio:checked');
    var default_color = themecolor.find('input#default_colors').val();
    colorInput.val(default_color);
    apply_color_changes();
    paletteSelected.prop('checked', false);
    themecolor.find('div.colorSelector').slideUp('fast');
    themecolor.find('div.paletteSelector').slideDown('fast');
});

themecolor.find('button#revertBtn').on("click", function() {
    var paletteSelected = themecolor.find('input[name="palette"]:radio:checked');
    var previous_color = themecolor.find('input#previous_colors').val();
    colorInput.val(previous_color);
    apply_color_changes();
    paletteSelected.prop('checked', false);
    themecolor.find('div.colorSelector').slideUp('fast');
    themecolor.find('div.paletteSelector').slideDown('fast');
});
