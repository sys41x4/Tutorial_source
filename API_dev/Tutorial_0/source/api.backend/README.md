# API.BACKEND
---

!!! Important !!!

1. You should modify the file config.json according to `config` directory path
2. By default the application will look into `/etc/test.app/config/config.json` which if you want can modify it in the source-code of `app.py`

---

-- API Endpoints --

```text
<host>:<port>/api/ : Show current api version
<host>:<port>/api/scrape : Scrape data from local/remote database
    [GET Args]
    scrape_type = user/db/live | Mandatory
    randomize = 0/1 | Optional
    count = >=0 | Optional
    action = fetch/update | Optional
    uid = <user_uid> | Optional
    email = <user_mailID> | Optional
    db_columns = [<db_col_0>, <db_col_2> ,...] | Optional

    These Args can be used together to fetch/modify data using the API endpoints
    
    Example : http://172.16.91.131:8080/api/scrape?scrape_type=user&randomize=1&count=6&action=fetch
              This will url will fetch data of 6 users in random orders from the local connected database

              http://172.16.91.131:8080/api/scrape?scrape_type=user&email=knut.normann@example.com&count=6&action=fetch
              This will fetch data of user having email nut.normann@example.com

              http://172.16.91.131:8080/api/scrape?scrape_type=user&db_columns=user.uid,user.email&randomize=1&count=3&action=fetch
              This will fetch particularly the column user.uid and user.email, with randomization enabled
              * To get all the data use * as a value of db_columns *

<host>:<port>/api/coordinates : Coordinates calculation
    origin = x,y | Mandatory
    coordinates = (x0,y0),(x1,y1),... | Optional
    reverse = 0/1 | Optional

    These Args can be used together to fetch/modify data using the API endpoints

    Example :
              http://172.16.91.131:8080/api/coordinates?origin=-69.8246,134.8719&coordinates=(54.6463,168.1213),(-89.2374,62.9537),(-38.6918,53.5376)&reverse=1
              This will fetch the descending coordinates list having origin -69.8246,134.8719
```
