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

app.get("/", (request, response) => {
  // if the user login already, redirect to the dashboard
  if (request.session.loggedin) {
    response.redirect("/dashboard");
  } else {
    response.sendFile(path.join(__static_html + "/login.html"));

  }

});

// express config for static files, json and other stuff
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "static")));
app.use(express.static(path.join(__dirname, "static/css")));
app.use(express.static(path.join(__dirname, "static/js")));
app.use(express.json());

// login post request
app.post("/", (request, response) => {

  try {
    let email = request.body.email;
    let password = request.body.password;
    if (email && password) {

      // incase we fk it up

      connection.query('SELECT * FROM users WHERE email = ? AND password = ?', [email, password], (error, results) => {
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


app.get('/userInfo', function (request, response) {

  if (request.session.loggedin) {

    let email = request.session.email;
    let sql = `SELECT role FROM users WHERE email = '${email}'`;
    connection.query
      (sql, (err, result) => {
        if (err) throw err;
        let role = request.session.role = result[0].role;
        let name = request.session.email.split("@")[0];
        response.json({ role: role, name: name });
      });
  }
  else { response.json({ error: "403 - Not Authenticated" }); }

})



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
  response.send(error, 404);
});

app.listen(port);