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

var random_color_radar = new Array();
for(var j = 0; j < event_name.length; j++) {
  var rd_str = "rgb(";
  for(var k = 0; k < 3; k++) {
    rd_str += (Math.floor(Math.random() * 255) + 1).toString() + ", "; //1~255 create random number
  }
  rd_str += "0.4)";
  random_color_radar[j] = rd_str;
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
					backgroundColor: random_color_radar,
					data: event_count
			}],
	},

  // Configuration options go here
  options: {
    responsive: false,
    scale: {
      gridLines: {
        color: "black",
        lineWidth: 1
      },
      angleLines: {
        display: false
      },
      ticks: {
        display: false,
        beginAtZero: true,
        min: 0,
        max: maxvalue + stepsize,
        stepSize: stepsize
      },
      pointLabels: {
        fontSize: 18,
        fontColor: "black"
      }
    },
    legend: {
      display: false
    },
    animation: {
      duration: 500,
      onComplete: function() {
        // You get the canvas context, to help you writing what you want
        var ctx = this.chart.ctx;

        // Here you set the context with what you need (font, size, color ...)
        ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontFamily, 'normal', Chart.defaults.global.defaultFontFamily);
        ctx.textAlign = 'center';
        ctx.fillStyle = 'black';

        this.data.datasets.forEach(function(dataset) {
            for (var i = 0; i < dataset.data.length; i++) {
                var model = dataset._meta[0].data[i]._model;
                ctx.fillText(dataset.data[i], model.x, model.y - 2);
            }
        });
      }
    }
  }
});
