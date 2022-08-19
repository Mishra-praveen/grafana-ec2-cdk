#!/bin/bash

echo "Installing docker, running  grafana container, configuring grafana"

#Install docker
yum update -y
yum install docker jq -y
usermod -a -G docker ec2-user
systemctl start docker
systemctl enable docker

#Running grafana container
REGION=$(curl http://169.254.169.254/latest/dynamic/instance-identity/document|grep region|awk -F\" '{print $4}')
GRAFANA_HOST="http://localhost:3000"
GRAFANA_USERNAME=admin
GRAFANA_PASSWORD=$(aws secretsmanager get-secret-value --region $REGION --secret-id grafana_pswd --query SecretString --output text)
docker run \
  --detach \
  --publish 3000:3000 \
  --name=grafana \
  --env "GF_SECURITY_ADMIN_PASSWORD=$GRAFANA_PASSWORD" \
  grafana/grafana

#configure datasource
cat > /tmp/datasource.json << EOF
{
  "name":"cloudwatch1",
  "type":"cloudwatch",
  "access":"proxy",
  "jsonData": {
    "authType": "default",
    "defaultRegion": "$REGION"
  }
}
EOF

#Wait for container to start
sleep 300

# Create Grafana datasource
curl -v -k $GRAFANA_HOST/api/datasources \
-u "$GRAFANA_USERNAME:$GRAFANA_PASSWORD" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d @/tmp/datasource.json

sleep 200
##Create Dashboard. Ref:  https://github.com/monitoringartist/grafana-aws-cloudwatch-dashboards
jq --version >/dev/null 2>&1 || { echo >&2 "I require jq but it's not installed.  Aborting."; exit 1; }
### Please edit grafana_* variables to match your Grafana setup:
grafana_host="http://localhost:3000"
grafana_cred="admin:${GRAFANA_PASSWORD}"
# Keep grafana_folder empty for adding the dashboards in "General" folder
grafana_folder="AWS"
ds=(1516 677 139 674 590 659 758 623 617 551 653 969 650 644 607 593 707 575 1519 581 584 2969 8050 11099 11154 11155 12979 13018 13040 13104 13892 14189 14391 14392 14954 14955 15016);
folderId=$(curl -s -k -u "$grafana_cred" $grafana_host/api/folders | jq -r --arg grafana_folder  "$grafana_folder" '.[] | select(.title==$grafana_folder).id')
if [ -z "$folderId" ] ; then echo "Didn't get folderId" ; else echo "Got folderId $folderId" ; fi
for d in "${ds[@]}"; do
  echo -n "Processing $d: "
  j=$(curl -s -k -u "$grafana_cred" $grafana_host/api/gnet/dashboards/$d | jq .json)
  payload="{\"dashboard\":$j,\"overwrite\":true"
  if [ ! -z "$folderId" ] ; then payload="${payload}, \"folderId\": $folderId }";  else payload="${payload} }" ; fi
  curl -s -k -u "$grafana_cred" -XPOST -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    $grafana_host/api/dashboards/import; echo ""
done