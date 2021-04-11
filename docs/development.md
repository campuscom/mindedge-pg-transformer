# Development
### Mindedge Course Transformer

- Create a virtual environment.

- Open Terminal (from project directory). After activating virtual environment, terminal will look something like this:

    `(.venv) user@<pc_name>:~/<path_to_work_directory>/marketplace-mindedge-transformer$`

    **Note:** Before installing requirements make sure you clone [marketplace-shared-lib](https://github.com/campuscom/marketplace-shared-lib) and [marketplace-shared-models](https://github.com/campuscom/marketplace-shared-models)
   to parent directory. This is only required for local development. Not needed using Docker setup.
   ```
    git clone git@github.com:campuscom/marketplace-shared-lib.git
    git clone git@github.com:campuscom/marketplace-shared-models.git
   ```
- Install requirements
  - `pip install -Ur requirements.txt`

- Create a `.env` file in project root directory (see `.env.example` for sample)

- Mongo and redis services from mindedge importer can be used or you can use docker to easily initiate again.

**Note:** Run with the importer-id generated after mindedge importer finish importing
```
python app.py --importer-id $importer-id
```