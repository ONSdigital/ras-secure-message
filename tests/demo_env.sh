
export VCAP_SERVICES='{
  "rds-static": [
   {
    "credentials": {
     "db_name": "oauth",
     "host": "rds-rmras-preprod.onsdigital.uk",
     "password": "a591d2aff645ac5993d9c7f1de896c66",
     "uri": "postgres://oauth:a591d2aff645ac5993d9c7f1de896c66@rds-rmras-preprod.onsdigital.uk:5432/oauth",
     "username": "oauth"
    },
    "label": "rds-static",
    "name": "oauth-db",
    "plan": "oauth-db",
    "provider": null,
    "syslog_drain_url": null,
    "tags": [
     "database",
     "RDS",
     "postgresql"
    ],
    "volume_mounts": []
   }
  ]
 }'


export VCAP_APPLICATION='{
  "application_id": "86f6b6c8-91c8-4d84-b996-390e6f9c045f",
  "application_name": "ras-django-preprod",
  "application_uris": [
   "ras-django-preprod.apps.prod.cf5.onsclofo.uk"
  ],
  "application_version": "c141d8dc-995f-4631-9e0d-1071ec06433d",
  "cf_api": "https://api.system.prod.cf5.onsclofo.uk",
  "limits": {
   "disk": 512,
   "fds": 16384,
   "mem": 512
  },
  "name": "ras-django-preprod",
  "space_id": "3baaaeab-16b7-4293-9462-ccc76a8c89cd",
  "space_name": "preprod",
  "uris": [
   "ras-django-preprod.apps.prod.cf5.onsclofo.uk"
  ],
  "users": null,
  "version": "c141d8dc-995f-4631-9e0d-1071ec06433d"
 }'


