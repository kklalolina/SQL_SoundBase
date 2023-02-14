from soundbase import create_app, db
from flask import g

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)