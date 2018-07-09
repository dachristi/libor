### Data Flow

A SQL database is used as the UI for the project and defines sources of
information (providers), email addresses of recipients, and storage for the
data that is collected (1-month LIBOR rate).


##### Step 1 - Scraping Data
The script first looks at the `providers` table in the libor database.  This
table contains the provider's full name (e.g. global_rates), a shorter name ---
up to 3 characters --- referred to as a tag (e.g. gr), the URL of the webpage
to scrape the data, and the status of that particular provider (enabled or
disabled).  The last field is important because custom parser methods need to be
created for each webpage that is parsed.  The webpage is simply stored as an
HTML file in a specified directory for later use.

##### Step 2 - Parsing Data
As mentioned earlier, custom methods created to parse each webpage.  In an effort to keep the class simple, the method to use id determined by the provider tag in the `providers` table.  The parse looks for 3 specific pieces of information: the 1-month LIBOR rate, the effective date, and the text that
the source uses to refers to the information.
Once the data has been successfully parsed, a function is called to store the
data in the database.

##### Step 3 - Emailing Data
