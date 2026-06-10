from app import create_app
from app.config import parse_bool

app = create_app()

if __name__ == "__main__":
    app.run(
        debug=parse_bool(
            app.config.get("DEBUG", "false"),
            default=False
        )
    )
    
