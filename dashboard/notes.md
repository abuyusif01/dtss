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
1. event can only be update once [done]

# fixes for production
1. fix login to redirect when pass not correct [done]
2. sync all port start from 8000 and ip address [done]
3. fix run command to show in a next window [done]
4. fix all pages and route make sure everything works
5. create an about page
6. fix update list
7. fix pie for terminal tab
