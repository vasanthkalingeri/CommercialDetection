$('#myTable tr').mouseenter(function(){
    $(this).css({ background: '#E8E8E8' });

}).mouseleave(function(){
    $(this).css({ background: '' });
});

function play(time)
{
	var myPlayer = videojs('mainvid');
	videojs("mainvid").ready(function(){
//          alert(myPlayer);
//          alert(time);
          // EXAMPLE: Start playing the video.
          myPlayer.play();
          myPlayer.currentTime(time);
          myPlayer.play();
    });
}

function get_secs(time_str)
{
    var times = time_str.split(':');
    var value = 0;
    for (var i in times)
        value += parseInt(times[i]) * Math.pow(60, 2 - i);     
    return value;
}

function add(start, end, start_str, id)
{
//    var new_end = prompt("Keep till?", end);
//    var index = id.parentNode.parentNode.rowIndex;
//    var table = document.getElementById("myTable");
//    var row = table.insertRow(index + 1);
//    var cells = [];
//    for (i=0;i<6;i++)
//        cells.push(row.insertCell(i));
//    var start = '{{item.0}}<input type="hidden" name="start{{item.3}}" value="{{item.0}}"></input>';
//    var end = '{{item.1}}<input type="hidden" name="end{{item.3}}" value="{{item.1}}"></input>';
//    var name = '<input type="text" name="name{{item.3}}" value="{{item.2}}" onchange="update(this.value, {{item.3}});"></input>';
//    var play = '<button type="button" onClick="play({{item.3}});" style="width:100%">Seek</button>';
//    var add = '<button type="button" onClick="add({{item.3}},{{item.4}}, this);" style="width:100%">+</button>';
//    var remove = '<button type="button" onClick="drop({{item.3}},{{item.4}}, this);" style="width:100%">-</button>';
//    var data = [start, end, name, play, add, remove];
//    
//    for (i=0;i<6;i++)
//        cells[i].innerHTML = data[i];

//    if(get_secs(new_end) > get_secs(end))
//    {
//        alert("Invalid range to split!!");
//        return;
//    }
    var sec_str = prompt("Split at ?", start_str);
    var secs = get_secs(sec_str);
    
    if(!((secs < end) && (secs > start)))
    {
        alert("Error: Split should be within start and end of the video segment !");
        return;
    }
    $.ajax({
        url : "add/", 
        type : "POST",
        dataType: "json", 
        data : {
            actual_start: start,
            start_sec : secs,
            end_sec : end
            },
        success : function(json) {
            $('#result').append( 'ServerResponse:' + json.server_response);
        },
        error : function(xhr,errmsg,err) {
            var a = "1";
        }
    });
    
    var ob = $("#output").load("/output/ #output");
//    ob.trigger("pagecreate");
    document.createStyleSheet('/static/output/output.css');
}

function drop(start, end, id)
{
    var index = id.parentNode.parentNode.rowIndex;
    var choice = prompt("Do you really want to delete this?(y/n)");
    if(choice == 'y')
        document.getElementById("myTable").deleteRow(index);
}

function update(text_data , start_secs)
{
    $.ajax({
        url : "update/", 
        type : "POST",
        dataType: "json", 
        data : {
            start : start_secs,
            text: text_data,
            },
        success : function(json) {
            $('#result').append( 'ServerResponse:' + json.server_response);
        },
        error : function(xhr,errmsg,err) {
            var a = "1";
        }
    });
}
