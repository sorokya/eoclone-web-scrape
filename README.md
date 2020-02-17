# EOClone Web Scrape

This script crawls all of the EOClone NPC data pages and generates
the eoserv configuration files for drops and shops.

I built this to compliment EOInfo. The drop and shop data can now be
integrated into that project.

This was built using [scrapy](https://github.com/scrapy/scrapy/)

# Running
* [install scrapy](https://github.com/scrapy/scrapy/#install)
* run `$ scrapy crawl npc` in the projects root directory

a drops.ini and shops.ini file will be output in the project root

