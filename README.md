# Libor Rate Distribution

These modules accomplish the task of scraping monthly Libor rates on a daily
basis from online sources, storing the data in a database, and sending a list of
recipients the data.

*libor_online.py - *This module scrapes the Libor rate from online sources and
stores the HTML as a file.

*libor_parse.py - *Parses the Libor rate from the HTML file and stores it in a SQL table.

*libor_send.sh - *Sends the Libor rate via email to a list of addresses.
