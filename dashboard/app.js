const port = 5000;
const mysql = require("mysql");
const { exec } = require("child_process");
const alert = require("alert");
const express = require("express");
const session = require("express-session");
const path = require("path");
const os = require("os");
const { fail } = require("assert");

os.hostname() === "The-Castle"
  ? (connection = mysql.createConnection({
    host: "127.0.0.1",
    user: "abuyusif01",
    password: "1111",
    database: "dtss",
  }))
  : (connection = mysql.createConnection({
    host: "127.0.0.1",
    user: "abuyusif",
    password: "hfST9bmsQeFWkaQS",
    database: "nodelogin",
  }));

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
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "static")));
app.use(express.static(path.join(__dirname, "static/css")));
app.use(express.static(path.join(__dirname, "static/js")));
app.use(express.json());


app.get("/", (request, response) => {
  // if the user login already, redirect to the dashboard
  if (request.session.loggedin) {
    response.redirect("/dashboard");
  } else {
    response.sendFile(path.join(__static_html + "/login.html"));

  }

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
        }
        else {
          if (results.length > 0) {
            request.session.loggedin = true;
            request.session.email = email;
            response.redirect("/dashboard");

          }
        }
      });
    }

  }
  catch (err) { }
});


app.get('/userInfo', (request, response) => {

  if (request.session.loggedin) {
    let email = request.session.email;
    let sql = `SELECT * FROM users WHERE Email = '${email}'`;
    connection.query(sql, (err, result) => {
      if (err) { response.json({ error: "40X - Something went wrong!!!" }); }
      request.session.role = result[0].Role;
      request.session.fname = result[0].Fname;
      request.session.lname = result[0].Lname;
      request.session.contact = result[0].Contact;

      let role = request.session.role;
      let fname = request.session.fname;
      let lname = request.session.lname;
      let contact = request.session.contact;
      response.json(
        {
          fname: fname,
          role: role,
          lname: lname,
          email: email,
          contact: contact
        }
      );
    });
  }
  else { response.json({ error: "403 - Not Authenticated" }); }

})

app.get("/execInfo", (request, response) => {

  if (!request.session.loggedin) {
    let sql = `SELECT * FROM commands`;
    connection.query(sql, (err, result) => {

      let success = parseInt(result[0].success);
      let fail = parseInt(result[0].failed);
      let pending = parseInt(result[0].pending);
      let count = parseInt(success + fail + pending).toString();
      let success_percent = parseInt((success / count) * 100).toString();
      let failed_percent = parseInt((fail / count) * 100).toString();
      let pending_percent = parseInt((pending / count) * 100).toString();

      response.json(
        {
          success: success,
          fail: fail,
          pending: pending,
          count: count,
          success_percent: success_percent,
          failed_percent: failed_percent,
          pending_percent: pending_percent

        }
      );
    });
  } else { response.json({ error: "403 - Not Authenticated" }); }
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

  let sql = `SELECT * FROM users WHERE Email = '${email}'`;
  connection.query(sql, (err, result) => {
    if (err) { response.json({ error: "40X - Something went wrong!!!" }); }
    let db_pass = result[0].Password;

    if (db_pass == current_password) {
      let sql = `UPDATE users SET Fname = '${fname}', Lname = '${lname}', Email = '${email}', Contact = '${contact}', Password = '${new_password}', Role = '${role}' WHERE Email = '${email}'`;
      connection.query(sql, (err, result) => {
        if (err) { response.json({ error: "40X - Something went wrong!!!" }); }
        alert("Password changed successfully");
      });
    }
    else {
      alert("Wrong password");
    }
  });
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
  if (request.session.role === "admin" || request.session.role === "Admin") {

    if (password == _password) {
      let sql = `INSERT INTO users (Fname, Lname, Email, Contact, Password, Role) VALUES ('${fname}', '${lname}', '${email}', '${contact}', '${password}', '${role}')`;
      connection.query(sql, (err, result) => {
        if (err) { response.json({ error: "40X - Something went wrong!!!" }); }
        alert("User added successfully");
      });
    }
    else { alert("Passwords don't match"); }
  }
  else { alert("Need to be admin first"); }
});


app.post("/exec_user", (request, response) => {

  if (!request.session.loggedin) {

    // add the command to pending commands table
    let sql_pending = `SELECT pending from commands`;
    connection.query(sql_pending, (err, result) => {
      let pending = parseInt(result[0].pending);
      let sql = `UPDATE commands SET pending = '${pending + 1}'`;
      connection.query(sql, (err, result) => { });
    });

    let command = request.body.command;
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
          alert(stderr);
          response.end();
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
          alert(stdout);
          response.end();
        }

      })
    } catch (error) { response.send(error); response.end() }
  }
  else {
    response.send('<script>alert("Need to login")</script>');
    response.end();
  }


});

// get on dashboard
app.get("/dashboard", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/index.html"));
  }
  else {
    response.sendFile(path.join(__static_html + "/login.html"));
    alert("Please login to view this page!");
    response.redirect("/");
  }
});

app.get("/terminal", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/terminal.html"));
  }
  else {
    alert("Please login to view this page!");
    response.redirect("/");
  }
});

app.get("/plc_info", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/plc_info.html"));
  }
  else {
    alert("Please login to view this page!");
    response.redirect("/");
  }
});

app.get("/events", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/events.html"));
  }
  else {
    alert("Please login to view this page!");
    response.redirect("/");
  }
});

app.get("/about", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/about.html"));
  }
  else {
    alert("Please login to view this page!");
    response.redirect("/");
  }
});

app.get("/settings", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/settings.html"));
  }
  else {
    alert("Please login to view this page!");
    response.redirect("/");
  }
});

app.get("/logout", (request, response) => {

  if (request.session.loggedin) {
    request.session.destroy();
    response.redirect("/");
  }
  else {
    response.redirect("/");
  }
});

app.get('*', function (request, response) {
  let error = `<h2>It appears that you are trying to access a page that doesn't exist. Please try again.
  below are the availeble pages:
  <br>
  /dashboard <br>
  /terminal <br>
  /plc_info <br>
  /events <br>
  /about <br>
  /setting </h2>
  `;
  response.send(error);
});

app.listen(port);