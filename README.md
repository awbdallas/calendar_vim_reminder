About
-----
Needed a small program to just run

Setup
-----
mv config_file.config.example config_file.config

Fill in all of the options under config. For my smtp server I ended up
just using Amazon ses for everything. The options are there so you can
change it to whatever you like.

Example Usage
-------------
./reminder.py

You can set it up to run in a cron job ever day. I personally have it set for
everyday at 7:00AM
