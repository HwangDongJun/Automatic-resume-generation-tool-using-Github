var topic_value = document.getElementById("topic_send_value").getAttribute('name');
var topic_split = topic_value.split('/'); //last value is null => delete
topic_split.pop();

var topic_name = new Array();
var topic_count = new Array();
for(var i = 0; i < topic_split.length; i++) {
  var detail_split = topic_split[i].split(',');
  topic_name[i] = detail_split[0];
  topic_count[i] = detail_split[1];
}

var random_color = new Array();
for(var j = 0; j < topic_name.length; j++) {
  var rd_str = "rgb(";
  for(var k = 0; k < 3; k++) {
    rd_str += (Math.floor(Math.random() * 255) + 1).toString() + ", "; //1~255 create random number
  }
  rd_str += "0.4)";
  random_color[j] = rd_str;
}

var ctx = document.getElementById('myBarChart').getContext('2d');
var chart = new Chart(ctx, {
  // The type of chart we want to create
  type: 'horizontalBar',

  // The data for our dataset
  data: {
			labels: topic_name,
			datasets: [{
					label: 'Frequently Used Topics',
					backgroundColor: random_color,
					data: topic_count
			}],
	},

  // Configuration options go here
  options: {
    responsive: false,
    scales: {
      xAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
});
