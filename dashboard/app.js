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


class Utils {

  constructor() {
    this.connection = connection;
  }

  assignRole(request, uname) {


  }
}
const __static_html = path.join(__dirname, "static").replace(/\\/g, "\\\\") + "/html";

// express config for static files, json and other stuff
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "static")));
app.use(express.static(path.join(__dirname, "static/html")));
app.use(express.static(path.join(__dirname, "static/css")));
app.use(express.static(path.join(__dirname, "static/js")));
app.use(express.json());


// display login page
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
  }
});

app.get("/terminal", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/terminal.html"));
  }
  else {
    response.sendFile(path.join(__static_html + "/login.html"));
  }
});

app.get("/plc_info", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/plc_info.html"));
  }
  else {
    response.sendFile(path.join(__static_html + "/login.html"));
  }
});

app.get("/events", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/events.html"));
  }
  else {
    response.sendFile(path.join(__static_html + "/login.html"));
  }
});

app.get("/about", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/about.html"));
  }
  else {
    response.sendFile(path.join(__static_html + "/login.html"));
  }
});

app.get("/settings", (request, response) => {
  if (request.session.loggedin) {
    response.sendFile(path.join(__static_html + "/settings.html"));
  }
  else {
    response.sendFile(path.join(__static_html + "/login.html"));
  }
});



app.listen(port);