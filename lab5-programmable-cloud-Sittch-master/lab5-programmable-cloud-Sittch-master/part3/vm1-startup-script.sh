attributes_url=http://metadata.google.internal/computeMetadata/v1/instance/attributes
mkdir -p /srv
cd /srv
curl $attributes_url/vm2-startup-script -H "Metadata-Flavor: Google" > vm2-startup-script.sh
curl $attributes_url/service-credentials -H "Metadata-Flavor: Google" > service-credentials.json
export GOOGLE_CLOUD_PROJECT= $(curl $attributes_url/project -H "Metadata-Flavor: Google")

pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib