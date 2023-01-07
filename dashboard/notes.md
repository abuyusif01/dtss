1. fix pie for terminal
2. create event tab
3. about me page
4. implement emailing system
5. recent updates 

# event 
each event will have a hash of its content to avoid tempararily storing the content in the database.

1. event id (hash) first 8 characters (sha256)
2. event description
3. event date and time
4. person triggered the event (IP address)


# db
create table events (time_stamp varchar(30), id varchar(70) not null, descr varchar(200), triggered_by varchar(20), priority varchar(20));


# generate events
1. login [done]
2. logout [done]
3. create account [done]
4. attack detection [done]


# rules
1. event can only be update once in 10m [done]

# fixes for production
1. fix login to redirect when pass not correct [done]
2. sync all port start from 8000 and ip addresses [done]
3. fix run command to show in next window [done]
4. fix all pages and route make sure everything works [done]
5. create an about page [done]
6. update list using data from db
7. creat pie for terminal tab [done]
8. fix setting pie [done]
9. after adduser redirect to dashboard [done]
10. render technical report to about page + theme it 
11. authentication for all routes [done]