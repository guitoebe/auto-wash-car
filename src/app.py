import sys
from pathlib import Path
import logging

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src import create_app

logging.debug('testee')

app = create_app()
if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        from src.models.customer import db
        db.create_all()
    app.run(debug=True)