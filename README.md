# NPO recommender system for course INFOMPPM at Utrecht University

When download the data used seperately from (TODO add SurfDrive link).

A short explination on each file and the order that it should be ran in if you were to redo all teh per processing:

1. HTMLScraper.ipynb: This file scaped the NPODataSet provides by the course teacher. The NPO dataset contains over 130.000 seperate html files. Therefore, running this code will take some time. When running you need to specify the folder with the html files. Code took approx 4 hours to finnisch  
2. DB2CSV.ipynb: This file will convert the scaped data into a more manageble csv file. Scaping is done to DB since we can stage changes and do writes to disk only at intervals to reduse I/O time by a lot.
3. 



# TODO when we have more time
1. Re-run the scaper with the backdrop images scraped. We found that some thumbnails are protected, and you need NPOPlus cookies in your browser to open them.
2. 
