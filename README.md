# Learning Journal

Learning Journal app developed using Pyramid and deployed on heroku.

##Deployment:

You can find this learning journal deployed on Heroku [here](https://amos-learning-journal.herokuapp.com/)


#Routes

- home: `/` will take you to the home page, a listing of journal entries 
- entry: `/journal/{ ID of Entry }` will take you a specific journal entry base on the ID that is given.
- create: `/journal/new-entry` will take you to a form to create an entry.
- edit: `journal/{ ID of Entry }/edit-entry` will take you to a (semi-functional) form pre-populated with the the specific journal entry base on the ID that is given.

## Authors:
- Maelle Vance
- Amos Boldor


# Tests:


## Python 2
```
=================================== test session starts ===================================
platform linux2 -- Python 2.7.12+, pytest-3.0.5, py-1.4.32, pluggy-0.4.0
rootdir: /home/x/codefellows/401/week3/learning_journal, inifile: pytest.ini
plugins: cov-2.4.0
collected 17 items 

learning_journal/tests.py .................

---------- coverage: platform linux2, python 2.7.12-final-0 ----------
Name                                       Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
learning_journal/__init__.py                   8      0   100%
learning_journal/models/__init__.py           22      0   100%
learning_journal/models/meta.py                5      0   100%
learning_journal/models/mymodel.py             9      0   100%
learning_journal/routes.py                     6      0   100%
learning_journal/scripts/__init__.py           0      0   100%
learning_journal/scripts/initializedb.py      30     18    40%   40-43, 47-64
learning_journal/views/__init__.py             0      0   100%
learning_journal/views/default.py             38      2    95%   15-16
learning_journal/views/notfound.py             4      2    50%   6-7
------------------------------------------------------------------------
TOTAL                                        122     22    82%


================================ 17 passed in 1.74 seconds ================================
```

## Python 3
```
=================================== test session starts ===================================
platform linux -- Python 3.5.2+, pytest-3.0.5, py-1.4.32, pluggy-0.4.0
rootdir: /home/x/codefellows/401/week3/learning_journal, inifile: pytest.ini
plugins: cov-2.4.0
collected 17 items 

learning_journal/tests.py .................

----------- coverage: platform linux, python 3.5.2-final-0 -----------
Name                                       Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
learning_journal/__init__.py                   8      0   100%
learning_journal/models/__init__.py           22      0   100%
learning_journal/models/meta.py                5      0   100%
learning_journal/models/mymodel.py             9      0   100%
learning_journal/routes.py                     6      0   100%
learning_journal/scripts/__init__.py           0      0   100%
learning_journal/scripts/initializedb.py      30     18    40%   40-43, 47-64
learning_journal/views/__init__.py             0      0   100%
learning_journal/views/default.py             38      2    95%   15-16
learning_journal/views/notfound.py             4      2    50%   6-7
------------------------------------------------------------------------
TOTAL                                        122     22    82%


================================ 17 passed in 2.09 seconds ================================


________________________________________ summary __________________________________________
  py27: commands succeeded
  py35: commands succeeded
  congratulations :)
```