const port = 5000;
const mysql = require("mysql");
const alert = require("alert");
const express = require("express");
const session = require("express-session");
const path = require("path");
const os = require("os");

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
    else {
      alert("Passwords don't match");
    }
  }
  else {
    alert("Need to be admin first");
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