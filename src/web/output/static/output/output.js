$('#myTable tr').mouseenter(function(){
    $(this).css({ background: '#E8E8E8' });

}).mouseleave(function(){
    $(this).css({ background: '' });
});


function play(time)
{
	var myPlayer = videojs('mainvid');
	videojs("mainvid").ready(function(){
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

function add(start, end, start_str)
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

function drop(start, end)
{
    if(confirm("Are you sure you want to remove this label ?"))
    {
        $.ajax({
            url : "delete/", 
            type : "POST",
            dataType: "json", 
            data : {
                start_sec : start,
                end_sec: end,
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
    var ob = $("#output").load("/output/ #output");
    document.createStyleSheet('/static/output/output.css');
}

function submit_form()
{
    document.updateForm.submit();
}
