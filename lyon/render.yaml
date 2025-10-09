services:
  - type: web
    name: lyon
    env: python
    plan: free
    buildCommand: "./build.sh"
    startCommand: "gunicorn lyon.wsgi:application"
    envVars:
      # Database from Render PostgreSQL
      - key: DATABASE_URL
        fromDatabase:
          name: lyondb
          property: connectionString

      # Django secret key
      - key: SECRET_KEY
        generateValue: true

      # Debug mode off for production
      - key: DEBUG
        value: false

      # Allowed hosts (adjust if you have a custom domain)
      - key: ALLOWED_HOSTS
        value: ".onrender.com"

      # Cloudinary credentials (replace <your_value> with actual keys)
      - key: CLOUDINARY_CLOUD_NAME
        value: "<your_cloud_name>"
      - key: CLOUDINARY_API_KEY
        value: "<your_api_key>"
      - key: CLOUDINARY_API_SECRET
        value: "<your_api_secret>"

databases:
  - name: lyondb
    plan: free
