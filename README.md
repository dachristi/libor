# Libor Rate Distribution

This project looks up the most recently posted (and free) LIBOR value from multiple sources.  The values are stored in a MySQL table and distributed via Gmail.

Contents of this repository the Python modules and MySQL database schema.


*content.py - *This module scrapes the Libor rate from online sources and
stores the HTML as a file.

*recipients.py reads email addresses from the table and distributes the email.
