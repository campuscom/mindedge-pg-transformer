# marketplace-mindedge-transformer
### Using Docker
#### If Mindegde Importer's docker services are running then below command will only initiate `mindedge_transformer` service

Update the importer_id=$importer_id & SSH key settings
Note: `importer_id` must taken form mindedge importer
```
docker-compose up -d
```
If mindedge importer mongo, redis service are not running then update the `docer-compose.yml` file uncomment
`mongo` and `redis` service then run the above command.
