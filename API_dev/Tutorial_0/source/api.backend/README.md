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
    scrape_type=user/db/live | Mandatory
    randomize=0/1 | Optional
    count=>=0 | Optional
    action=fetch/update | Optional

    These Args can be used together to fetch/modify data using the API endpoints
    
    Example : http://172.16.91.131:8080/api/scrape?scrape_type=user&randomize=1&count=6&action=fetch
              This will url will fetch data of 6 users in random orders from the local connected database
```
