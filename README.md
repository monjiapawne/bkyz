# bkyz

## Flask

```sh
flask run
flask db migrate {name}
flask db upgrade

# Nuke db 
rm instance/bkyz.db
rm migrations/versions/*.py
flask db migrate -m "initial schema"
flask db upgrade
```