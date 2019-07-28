var topic_value = document.getElementById("topic_send_value").getAttribute('name');
var topic_split = topic_value.split('/'); //last value is null => delete
topic_split.pop();

var topic_box = new Array();
for(var i = 0; i < topic_split.length; i++) {
  var detail_split = topic_split[i].split(',');
  var topic_dict = {};

  topic_dict['y'] = parseInt(detail_split[1]);
  topic_dict['label'] = detail_split[0];
  topic_box[i] = topic_dict;
}

var random_color = new Array();
for(var j = 0; j < topic_box.length; j++) {
  var rd_str = "rgb(";
  for(var k = 0; k < 3; k++) {
    rd_str += (Math.floor(Math.random() * 255) + 1).toString() + ", "; //1~255 create random number
  }
  rd_str += "0.4)";
  random_color[j] = rd_str;
}

window.onload = function() {
  CanvasJS.addColorSet("custom_color", random_color)
  var chart = new CanvasJS.Chart("chartContainer", {
    colorSet: "custom_color", // random color 추출
  	animationEnabled: true,
  	data: [{
  		type: "pie",
  		startAngle: 240,
      indexLabelFontSize: 18,
  		yValueFormatString: "##0\"times\"",
  		indexLabel: "{label} - {y}",
  		dataPoints: topic_box
  	}]
  });
  chart.render();
}
