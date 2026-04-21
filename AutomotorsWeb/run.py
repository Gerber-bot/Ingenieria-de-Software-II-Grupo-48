from app import create_app

app = create_app()

if __name__ == '__main__':
    # Habilitamos el modo debug para facilitar el desarrollo
    app.run(debug=True, port=5000)