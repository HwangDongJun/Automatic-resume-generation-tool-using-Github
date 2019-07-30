var express = require('express');
var main = express();

var fs = require('fs');

var bodyParser = require('body-parser');
main.use(bodyParser.urlencoded({ extended: false }));

var mysql = require('mysql');
var conn = mysql.createConnection({
	host : 'localhost',
	user : 'root',
	password : 'ehdwns20',
	database : 'githubuser'
});

conn.connect();

main.locals.pretty = true;
//setting jade
main.set('views', './views');
main.set('view engine', 'jade');

main.get('/page/main_page', (req, res) => {
	res.render('main_page');
});

//setting css path
var path = require('path');
main.use(express.static(path.join(__dirname, '/')));

main.post('/page', (req, res) => {
	var ps = require('python-shell');
	var user_email = req.body.email;
	var user_pwd = req.body.pwd;
	var user_name = req.body.name;
	var name = req.body.Uname;
	var insert_sql = 'INSERT INTO user (username) VALUES ("' + user_name + '")';
	var select_sql = 'SELECT count(*) FROM user WHERE username = "' + user_name + '"';
	//중복 이름 발생시 확인한 다음 추가하지 않는다.

	conn.query(select_sql, (err, rows, fields) => {
		if(err) {
			console.log(err);
		} else {
			var count = rows[0]['count(*)'];
			if(count == 0) {
				conn.query(insert_sql, (err, rows, fields) => {
					if(err) {
						console.log(err);
					} else {
						console.log(rows.insertId);
					}
				});
			}
		}
	});
	//중복처리될 경우 user table에는 이름을 추가하지 않는다.

	var options = {
		mode: 'text',
		pythonPath: '',
		pythonOptions: ['-u'],
		scriptPath: '',
		args: [user_email + ':' + user_pwd, user_name, name] // 입력받은 github email and password를 넣는다.
	};

	ps.PythonShell.run('./python_file/main.py', options, (err, results) => {
		if(err) throw err;
		res.redirect('/page/' + user_name);
	});
});

main.get('/page/:name', (req, res) => {
	var Uname = req.params.name;
	fs.readFile('./python_file/user_profile/info_dict_'+Uname+'.json', {encoding:'utf8'}, (err, data) => {
		console.log(data);
		var Uprivacy = JSON.parse(data);
		//console.log(Uprivacy);

		var topic_count = Uprivacy.repos_topic;
		var topic_str = "";
		for ( var key in topic_count ) {
			topic_str += key + ',' + topic_count[key] + '/';
		}
		var event_count = Uprivacy.user_event;
		var event_str = "";
		for (var key in event_count) {
			event_str += key + ',' + event_count[key] + '/';
		}

		res.render('profile', {privacy:Uprivacy, topics:topic_str, events:event_str, name: Uname + "'s Github Profile!"});
	});
});

main.listen(3306, () => {
	console.log('Connected, 3306 port!');
});
