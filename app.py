from waitress import serve

from routes import app


if __name__ == "__main__":
    # app.run(host='localhost', port=5000, debug=True)
    serve(app, host='localhost', port=5000)
