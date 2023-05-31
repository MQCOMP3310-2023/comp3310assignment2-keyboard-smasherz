from project import create_app
from flask_security import Security, SQLAlchemyUserDatastore
from project import db
from project.models import user, Role

if __name__ == '__main__':
  app = create_app()
  user_datastore = SQLAlchemyUserDatastore(db, user, Role)
  security = Security(app, user_datastore)
  app.run(host = '0.0.0.0', port = 8000, debug=False) #debug changed from true to false (CodeQL fix)