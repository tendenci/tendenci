//dynamic line form creation
function updateIndex(e, prefix, idx){
    var id_regex = new RegExp('('+ prefix +'-\\d+)');
    var replacement = prefix + '-' + idx
    if ($(e).attr("for")) 
        {$(e).attr("for", $(e).attr("for").replace(id_regex, replacement));}
    if (e.id) {e.id = e.id.replace(id_regex, replacement);}
    if (e.name){ e.name = e.name.replace(id_regex, replacement);}
}

function addLine(prefix, data){
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    var row = $('#line-hidden').clone(true).get(0);
    
    // place proper class
    $(row).addClass('line-form');
    
    // update id attr
    var replacement = prefix + '_' + formCount
    $(row).attr('id',replacement);
    
    $(row).find("input").each(function() {
        updateIndex(this, prefix, formCount);
        if($(this).attr("name")==(prefix+"-"+formCount+"-x1")){
            $(this).val(data['x1']);
        } else if($(this).attr("name")==(prefix+"-"+formCount+"-y1")){
            $(this).val(data['y1']);
        } else if($(this).attr("name")==(prefix+"-"+formCount+"-x2")){
            $(this).val(data['x2']);
        } else if($(this).attr("name")==(prefix+"-"+formCount+"-y2")){
            $(this).val(data['y2']);
        }
    });
    
    // insert as last element into form list
    $('#lines-formset').append(row);
    
    $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
    
    return false;
}

function updateLastLine(data){
    var last_line = $('#lines_0');
    var first_line = $('#lines_1');
    last_line.find('.x2').val(first_line.find('.x1').val());
    last_line.find('.y2').val(first_line.find('.y1').val());
    last_line.find('.x1').val(data['x2']);
    last_line.find('.y1').val(data['y2']);
}

// drawing
function redrawMap(map){
    var lines = $(".line-form");
    $(map).clearCanvas();
    $(map).drawImage({
        source: "{{ map.file.url }}",
        x: 0, y: 0,
        width: 900,
        fromCenter: false,
    });
    lines.each(function(i){
        var x1 = $(this).find('.x1').val();
        var y1 = $(this).find('.y1').val();
        var x2 = $(this).find('.x2').val();
        var y2 = $(this).find('.y2').val();
        $(map).drawLine({
            strokeStyle: "#000000",
            strokeWidth: 10,
            strokeCap: "round",
            strokeJoin: "miter",
            x1: x1, y1: y1,
            x2: x2, y2: y2,
        });
    });
}

$(document).ready(function(){
    // initialize map image
    $("canvas").drawImage({
        source: "{{ map.file.url }}",
        x: 0, y: 0,
        width: 900,
        fromCenter: false,
    });
    
    // initialize last line
    addLine('lines', {});
    
    //state variables for plotting
    prev_x = null;
    prev_y = null;

    //line plotting
    $("canvas").click(function(e){
        var position = $(this).position();
        var offset = $(this).offset();
        var x = e.pageX - (offset.left);
        var y = e.pageY - (offset.top);
        $("canvas").drawPolygon({
          fillStyle: "black",
          x: x, y: y,
          radius: 5,
          sides: 4,
        })
        if (prev_x){
            //initialize a line form here
            var data = {
                'x1':prev_x,
                'y1':prev_y,
                'x2':x,
                'y2':y,
            }
            addLine('lines', data);
            updateLastLine(data);
            redrawMap(this);
        }
        prev_x = x;
        prev_y = y;
    });
});
