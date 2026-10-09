# Data Analytics - Capstone Project

Welcome to your final step! You are now tasked with completing a full data analytics project using the skills you gained in the past months.


## Project Structure

The project submission should be comprised of the following:
* A small deck (max 5 slides), showcasing the problem at hand, the process used to solve it and the tools/technologies used
* One (or more) **Python notebook**, that shows all the relevant analysis steps, including data fetching, cleaning, EDA, clustering and relevant charts; at a minimum, the project should also contain two of the following:
  * Advanced charting
  * Hypothesis test
  * Regression
  * Web scraping
  * Additional data integration
  * Classification (bonus)
* A Power BI dashboard, to showcase the final results story telling and conclusions; this can also include further processing steps via PowerQuery, if needed

All of the above must be versioned in a git repository hosted on GitHub.
The submission must be shared with `luca.terrazzan@boolean.careers` via email and within the deadline specified at lesson and on Discord (usually two Sundays after the last lesson). It can either be a zipped Git repository or a link to a public GitHub repository (preferred).


## Track

The track contains a certain level of ambiguity; goals might be unclear, information could be missing. This is intended!

You need to be able to investigate, solve and provide your own conclusions...just like in real projects!


### ISTAT traffic analysis

Your company works in road traffic management and risk prevention, and asked you to create an updated dashboard of the best Italian municipalities to invest into. After discussing with the business, you decide that you need to know what are the places with the highest ratio of car accidents in the latest years, with an option for forecasting. The data at our current disposal is unreliable, outdated and too dirty to work with.

The goal: being able to see what towns have the highest accidents rates, total accidents, population and any other statistic that might be meaningful to our business goal! E.g.: what are the best cities to invest into? Why?


#### Data sources

After some investigation, you discovered that you can find the raw data via the official API of ISTAT and SITUAS.

For traffic accidents statistics, you find the endpoint `https://esploradati.istat.it/SDMXWS/rest/data/41_983`. This data will be updated every few months, so it needs to be fetched automatically.

HINT: the provided URL exposes an XML dataset; to get a CSV instead, you can use the http header {'Accept': 'application/vnd.sdmx.data+csv;version=1.0.0'}

However, some data needs to be joined with a different data source to get the area name (column `REF_AREA`).

Also, we realize that the ISTAT table does not have the area population; we need that also to calculate the per capita accident ratio.

Additionally, your company is interested in understanding which are the cities with the highest accidents rate density per square km.

Fortunately, we can get both information from SITUAS at the webpage `https://situas.istat.it/web/#/territorio/body?id=74&dateFrom=2020-12-31`. This data is static, so it's fine to download it manually once and store the `.csv` in your project. (bonus points if you scrape it instead!). Careful though, the csv is year specific, take a closer look at the content!

Take some time to read through the different columns and understand what kind of information is included. E.g.: what's the meaning of `DATA_TYPE`? What's the meaning of `OBS_VALUE`?
Look online for additional clues to the different columns meaning, if needed!

Want to find other relevant data to enrich the CSV? Go for it!


#### Process

At a minimum, complete the following steps:

* Make sure you understand the underlying data sets; **if unsure, use your tutoring resources! Wrong interpretations might lead to incorrect analyses!**
* Automatically fetch and clean up the needed data; HINT: look and explain extreme values/outliers
* Perform EDA and display related charts
* Create an enriched resulting data set
* Perform any needed analysis, create the relevant new columns (i.e.: # per capita accidents)
* Attempt at enriching your data set with clustering groups that highlight cities based on selected features
* Perform a relevant statistical/ML analysis that could realistically provide valuable information
* Create a PowerBI dashboard that provides a neat story telling


### Custom Track

If you already have an awesome project idea, contact Luca Terrazzan on Discord and we will go over a possible adaptation of your own project.

All of the previous requirements should be applicable to your proposal.


### Hints and tips

Only available in the lesson recording... 👀
