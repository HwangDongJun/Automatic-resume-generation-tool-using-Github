var event_value = document.getElementById("event_send_value").getAttribute('name');
var event_split = event_value.split('/'); //last value is null => delete
event_split.pop();

var event_name = new Array();
var event_count = new Array();
for(var i = 0; i < event_split.length; i++) {
  var detail_split = event_split[i].split(',');
  event_name[i] = detail_split[0];
  event_count[i] = detail_split[1];
}

var random_color = new Array();
for(var j = 0; j < event_name.length; j++) {
  var rd_str = "rgb(";
  for(var k = 0; k < 3; k++) {
    rd_str += (Math.floor(Math.random() * 255) + 1).toString() + ", "; //1~255 create random number
  }
  rd_str += "0.4)";
  random_color[j] = rd_str;
}

var maxvalue = Math.max.apply(null, event_count);
var stepsize = parseInt(maxvalue / 4);

var ctx = document.getElementById('myRadarChart').getContext('2d');
var chart = new Chart(ctx, {
  // The type of chart we want to create
  type: 'radar',

  // The data for our dataset
  data: {
			labels: event_name,
			datasets: [{
					label: 'User Events',
					backgroundColor: random_color,
					data: event_count
			}],
	},

  // Configuration options go here
  options: {
    responsive: false,
    scale: {
    gridLines: {
      color: "black",
      lineWidth: 3
    },
    angleLines: {
      display: false
    },
    ticks: {
      beginAtZero: true,
      min: 0,
      max: maxvalue,
      stepSize: stepsize
    },
    pointLabels: {
      fontSize: 18,
      fontColor: "black"
    }
    },
    legend: {
      position: 'left'
    }
  }
});
