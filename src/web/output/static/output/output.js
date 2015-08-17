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

function submit_form()
{
    document.updateForm.submit();
}
