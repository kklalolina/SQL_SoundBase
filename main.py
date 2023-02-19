from soundbase import create_app, register_blueprints

app = create_app()

if __name__ == '__main__':
    app = register_blueprints(app)
    app.run(debug=True)