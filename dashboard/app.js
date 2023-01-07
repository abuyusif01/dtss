const mysql = require("mysql");
const {
  exec
} = require("child_process");
const alert = require("alert");
const express = require("express");
const session = require("express-session");
const path = require("path");
const dotenv = require("dotenv");
var crypto = require('crypto');

dotenv.config();

const port = process.env.PORT;

const connection = mysql.createConnection({
  host: process.env.DB_ADDR,
  user: process.env.USER,
  password: process.env.DB_PASSWD,
  database: process.env.DB_NAME,
});

const app = express();
app.use(
  session({
    secret: "secret",
    resave: true,
    saveUninitialized: true,
  })
);

const __static_html = path.join(__dirname, "static").replace(/\\/g, "\\\\") + "/html";

// express config for static files, json and other stuff
app.use(express.json());
app.use(express.urlencoded({
  extended: true
}));
app.use(express.static(path.join(__dirname, "static")));
app.use(express.static(path.join(__dirname, "static/css")));
app.use(express.static(path.join(__dirname, "static/js")));
app.use(express.json());

app.get('/get_events', (req, res) => {

  if (req.session.loggedin) {
    connection.query('SELECT * FROM events', (error, results) => {
      if (error) {
        console.log(error);
        res.end();
      } else { res.send(results); }
    });
  } else { res.redirect("/"); }
});

app.get('/events_count', (req, res) => {

  if (req.session.loggedin) {
    connection.query('SELECT COUNT(*) FROM events', (error, results) => {
      if (error) {
        console.log(error);
      } else {
        let result = results[0]['COUNT(*)'].toString();
        res.json({
          events_count: result
        });
      }
    });
  } else { res.redirect("/"); }
});

app.get("/", (request, response) => {
  // if the user login already, redirect to the dashboard
  if (request.session.loggedin) {
    response.redirect("/dashboard");
  } else { response.sendFile(path.join(__static_html + "/login.html")); }
});

// login post request
app.post("/", (request, response) => {

  try {
    let email = request.body.email;
    let password = request.body.password;
    if (email && password) {

      connection.query('SELECT * FROM users WHERE Email = ? AND Password = ?', [email, password], (error, results) => {
        if (error) {
          response.redirect("/");
          console.log(error);
          response.end();
        } else {
          if (results.length > 0) {
            request.session.loggedin = true;
            request.session.email = email;
            response.redirect("/dashboard");

            let now = new Date().toLocaleString("en-GB", {
              timeZone: "Asia/Kuala_Lumpur"
            }, {
              hour12: false
            }).replace(/, /g, ' ').replaceAll('/', '-');
            let id_hash = crypto.createHash('sha256').update(now).digest('hex');
            let description = "User logged in";
            let trigger = email;
            let priority = "INFO";
            let sql = `INSERT INTO events values ('${now}', '${id_hash}', '${description}', '${trigger}', '${priority}');`;
            connection.query(sql, (err, result) => { });
          } else { response.redirect("/"); }
        }
      });
    }
  } catch (err) { }
});

app.get('/userInfo', (request, response) => {

  if (request.session.loggedin) {
    let email = request.session.email;
    let sql = `SELECT * FROM users WHERE Email = '${email}'`;
    connection.query(sql, (err, result) => {
      if (err) {
        response.json({
          error: "40X - Something went wrong!!!"
        });
      }
      request.session.role = result[0].Role;
      request.session.fname = result[0].Fname;
      request.session.lname = result[0].Lname;
      request.session.contact = result[0].Contact;

      let role = request.session.role;
      let fname = request.session.fname;
      let lname = request.session.lname;
      let contact = request.session.contact;
      response.json({
        fname: fname,
        role: role,
        lname: lname,
        email: email,
        contact: contact
      });
    });
  } else {
    response.json({
      error: "403 - Not Authenticated"
    });
  }

})

app.get("/execInfo", (request, response) => {

  if (request.session.loggedin) {
    let sql = `SELECT * FROM commands`;
    connection.query(sql, (err, result) => {

      let success = parseInt(result[0].success);
      let fail = parseInt(result[0].failed);
      let pending = parseInt(result[0].pending);
      let count = parseInt(success + fail + pending).toString();
      let success_percent = parseInt((success / count) * 100).toString();
      let failed_percent = parseInt((fail / count) * 100).toString();
      let pending_percent = parseInt((pending / count) * 100).toString();

      response.json({
        success: success,
        fail: fail,
        pending: pending,
        count: count,
        success_percent: success_percent,
        failed_percent: failed_percent,
        pending_percent: pending_percent

      });
    });
  } else {
    response.json({
      error: "403 - Not Authenticated"
    });
  }
});

app.post("/personal_info", (request, response) => {

  let fname = request.body.fname;
  let lname = request.body.lname;
  let email = request.body.email;
  let contact = request.body.contact;
  let current_password = request.body.current_password;
  let new_password = request.body.new_password;
  let role = request.body._role;

  // get user password from the database to check if the user is the owner of the account or not
  // then update the info if everything is ok

  // make sure the user is admin

  if (!request.session.loggedin) {
    response.redirect("/");
  } else {
    let sql = `SELECT * FROM users WHERE Email = '${email}'`;
    connection.query(sql, (err, result) => {
      if (err) {
        response.json({
          error: "40X - Something went wrong!!!"
        });
      }
      let db_pass = result[0].Password;
      if (db_pass == current_password) {
        let sql =
          `UPDATE users SET Fname = '${fname}', Lname = '${lname}', Email = '${email}', Contact = '${contact}', Password = '${new_password}', Role = '${role}' WHERE Email = '${email}'`;
        connection.query(sql, (err, result) => {
          if (err) {
            response.json({
              error: "40X - Something went wrong!!!"
            });
          }
          response.send("<script> alert('Updated Successfully'); window.location.href = '/dashboard'; </script>")
        });
      } else {
        response.send("<script> alert('Wrong Password'); window.location.href = '/settings'; </script>")
      }
    });
  }
});

app.post("/add_users", (request, response) => {
  let fname = request.body.fname;
  let lname = request.body.lname;
  let email = request.body.email;
  let role = request.body._role;
  let contact = request.body.contact;
  let _password = request.body._password;
  let password = request.body.password;

  // make sure the user is admin
  if (!request.session.loggedin) {
    response.redirect("/");
  } else {
    if (request.session.role === "admin" || request.session.role === "Admin") {
      if (password == _password) {
        let sql =
          `INSERT INTO users (Fname, Lname, Email, Contact, Password, Role) VALUES ('${fname}', '${lname}', '${email}', '${contact}', '${password}', '${role}')`;
        connection.query(sql, (err, result) => {
          if (err) {
            response.json({
              error: "40X - Something went wrong!!!"
            });
          }
          response.send("<script> alert('User Created Successfully'); window.location.href = '/dashboard'; </script>")
          // update the event table to show that a new user has been added same as the one in utill.py
          let now = new Date().toISOString().slice(0, 19).replace('T', ' ');

          let id_hash = crypto.createHash('sha256').update(now).digest('hex');
          let description = "New user added";
          let trigger = "Admin";
          let priority = "INFO";

          let sql = `INSERT INTO events values ('${now}', '${id_hash}', '${description}', '${trigger}', '${priority}');`;
          connection.query(sql, (err, result) => { if (err) { console.log(err); } });
        });
      } else { response.send("<script> alert('Password not matched'); window.location.href = '/settings'; </script>") }
    } else { response.send("<script> alert('Needs to be admin first'); window.location.href = '/dashboard'; </script>") }
  }
});

app.post("/exec", (request, response) => {

  if (request.session.loggedin) {
    if (request.body._root) {
      if (request.session.role === "admin" || request.session.role === "Admin") {
        command = `echo ${process.env.ROOT_PASSWD} | sudo -S ${request.body._root} 0>/dev/null`
      } else {
        alert("Only admins are allowd to run commands as root");
        response.redirect("/terminal");
        return;
      }
    } else { command = request.body._user; }

    // add the command to pending commands table
    let sql_pending = `SELECT pending from commands`;
    connection.query(sql_pending, (err, result) => {
      let pending = parseInt(result[0].pending);
      let sql = `UPDATE commands SET pending = '${pending + 1}'`;
      connection.query(sql, (err, result) => { });
    });

    try {
      exec(command, (error, stdout, stderr) => {

        if (error || stderr) {
          let sql_pending = `SELECT pending from commands`;
          connection.query(sql_pending, (err, result) => {
            let _pending = parseInt(result[0].pending);
            let sql = `UPDATE commands SET pending = '${_pending - 1}'`;
            connection.query(sql, (err, result) => { });
          });

          let sql_failed = `SELECT failed from commands`;
          connection.query(sql_failed, (err, result) => {
            let _failed = parseInt(result[0].failed);
            let sql = `UPDATE commands SET failed = '${_failed + 1}'`;
            connection.query(sql, (err, result) => { });
          });
          response.send(`<pre>${error || stderr}</pre>`);
        }

        if (stdout) {
          let sql_pending = `SELECT pending from commands`;
          connection.query(sql_pending, (err, result) => {
            let _pending = parseInt(result[0].pending);
            let sql = `UPDATE commands SET pending = '${_pending - 1}'`;
            connection.query(sql, (err, result) => { });
          });

          let sql_success = `SELECT success from commands`;
          connection.query(sql_success, (err, result) => {
            let _success = parseInt(result[0].success);
            let sql = `UPDATE commands SET success = '${_success + 1}'`;
            connection.query(sql, (err, result) => { });
          });

          response.send(`<pre>${stdout}</pre>`);
        }
      })
    } catch (error) {
      response.send(`<pre>${error}</pre>`);
      response.end()
    }
  } else { response.redirect("/"); }
});

// get on dashboard
app.get("/dashboard", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/index.html"));
  } else {
    response.sendFile(path.join(__static_html + "/login.html"));
    response.redirect("/");
  }
});

app.get("/terminal", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/terminal.html"));
  } else { response.redirect("/"); }
});

app.get("/plc_info", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/plc_info.html"));
  } else { response.redirect("/"); }
});

app.get("/events", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/events.html"));
  } else { response.redirect("/"); }
});

app.get("/about", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/about.html"));
  } else { response.redirect("/"); }
});

app.get("/settings", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/settings.html"));
  } else { response.redirect("/"); }
});

app.get("/logout", (request, response) => {

  if (request.session.loggedin) {
    request.session.destroy();
    response.redirect("/");
  } else { response.redirect("/"); }
});

app.get('*', function (request, response) {
  let error = `<h2>It appears that you are trying to access a page that doesn't exist. Please try again.
  below are the availeble pages: </h2>

  <h4>
  /dashboard <br>
  /terminal <br>
  /plc_info <br>
  /events <br>
  /about <br>
  /setting </h4>
  `;
  response.send(error);
});

app.listen(port);