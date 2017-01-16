# Learning Journal

Learning Journal app developed using Pyramid and deployed on heroku.

##Deployment:

You can find this learning journal deployed on Heroku [here](https://amos-learning-journal.herokuapp.com/)


#Routes

- home: `/` will take you to the home page, a listing of journal entries.
- entry: `/journal/{ ID of Entry }` will take you a specific journal entry base on the ID that is given.
- create: `/journal/new-entry` will take you to a form to create an entry.
- edit: `journal/{ ID of Entry }/edit-entry` will take you to a (semi-functional) form pre-populated with the the specific journal entry base on the ID that is given.
- login: `/login` GET request gets you the login page and POST will try to log you in.
- logout: `/logout` GET request logs you out.
- api_list: `/api/entries` GET request will return JSON of all the entries in the Database.

## Authors:
- Maelle Vance
- Amos Boldor