# Sri Lankan Actors/Actresses Search Engine

Source codes for a search engine made by using Elastic Search and python for searching Actors and Actresses in Sri Lanka.

## Getting Started

Wait after the following command until the elastic search and flask application starts.

```bash
on cmd-> start.bat
```
## Fields and Metadata
### Text Fields
* Name
* Real Name
* Birthday
* Date of death
* Address
* Biography
* Awards
  * Award Name
  * Award Festival Name
* Movie
  * Movie Title
  * Role
### Metadata
* Votes
* Ratings

## Supported Queries
* Search the actors by text fields
  * Ex: Gamini Fonseka, ගාමිණි ෆොන්සේකා, Sarasaviya Awards, 1975, Rekava
* Range Search
  * Ex: Top 10 actors, හොඳම නළුවන් 10
* Filter Results by Award name, Award Festival, Movie Title, Movie role
  * Ex: හොඳම නළුවන් 20 filter by නිළියන්
* Search with mispelled words
  * Ex: 'viajaay' or 'විජයා'  will give results belongs to vijaya

## Features
* Both Sinhala and English can be used for searching
* Automatically identifies keywords like 'top', 'best', 'හොඳම' and change results accordingly
* Search will work for mispelled words
* Range query support
* Results are preprocessed before displaying


## Scraping and other Information
For scraping films.lk website was used. 
[FILMS.LK](https://films.lk).
Python Beautiful Soup was used for data scraping and the source code can be found here.

Google Translate was used for translation. 