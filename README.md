To Do List Website

This To Do List Website combines a few skills into one project.
I utilized flask, flask_sqlalchemy, werkzeug.security, and more to build a functional user 
based website!

How it Works:
It is a flask webpage, once running in terminal go to the link, from there the website will
prompt you to sign in with a valid email or password, if the email exists or isnt valid you can't
create an account, if it is, the method in charge of this will hash the password and store the
username into a SQL Database

From there, the user is able to go to the homepage where they can enter in tasks, order them
by importnace or date and delete and edit them

There is a logout button to log out, if the user is logged out they cannot access their tasks 
or any user needed pages

If they log back in all of their data is stored. The User table and Task table is joined on user.id
allowing this connection between user and tasks.

So each individual user is paired with their own individual tasks which they can access whenever 
they sign in!

The UI was fun to make and design, I am very happy with the finished product!
