# Project Structure- Mindedge Transformer
This is a python based project built with version 3.8. It might work with previous versions of Python, 
but that is not guaranteed.

1. **Entry point** - app.py

## Dependencies

Following are the primary dependencies worth noting:

1. MongoDB - [https://www.mongodb.com/](https://www.mongodb.com/)
2. MongoEngine - [http://mongoengine.org/](http://mongoengine.org/)
3. Marketplace Shared Library - [https://github.com/campuscom/marketplace-shared-lib](https://github.com/campuscom/marketplace-shared-lib)
4. Marketplace Shared Models (Mongo) - [https://github.com/campuscom/marketplace-shared-models](https://github.com/campuscom/marketplace-shared-models)
5. Campuscom Shared Models (Postgres) - [https://github.com/campuscom/campuscom-shared-models](https://github.com/campuscom/marketplace-shared-models)

Besides these there are few other dependencies that the project relies on. The full list of dependencies can be found in the `requirements.txt` included with the project.

### Purpose:
It sole purpose is to transform MindEdge imported data from MongoDB to Postgres.

**marketplace-shared-models** -> All related MongoDB table models stored here.

**campuscom-shared-models** -> All related Postgres table models stored here.

**marketplace-shared-lib** -> Common function required for all the importer and transformer written here.

There are 2 mappers are available
1. Course
2. Section

Their are `MindEdgeTransformer` class which will use the mappers to transform data to required 
format and save to database.

## TOC

| No     | Table of content |
| :-----------: | ----------------: |
| 1      | [Project Architecture](docs/architecture.md)  |
| 2      | [Local Development Guide](docs/development.md)  |
| 3      | [Dockerizing Guide](docs/dockerization.md)  |
| 4      | [Environment Variable List](docs/environment_variables.md)  |
| 5      | [Production Deploy Guide](docs/production.md)  
