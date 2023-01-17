#!/bin/bash
#Script to provision a new Azure ML workspace
grn=$'\e[1;32m'
end=$'\e[0m'

set -e

# Start of script
SECONDS=0
printf "${grn}Starting creation of workspace and aml infra resources...${end}\n"

# Source subscription ID, and prep config file
source sub.env
sub_id=$SUB_ID

# Set the default subscription 
az account set -s $sub_id

# Source unique name for RG, workspace creation
unique_name='doc-pipeline'
number=$[ ( $RANDOM % 10000 ) + 1 ]
resourcegroup=$unique_name$number
workspacename=$unique_name$number'ws'
cognitiveservice=$unique_name'fr'$number
location='westus'
endpoint="https://westus.api.cognitive.microsoft.com/"

# Create a resource group
printf "${grn}Starting creation of resource group...${end}\n"
rg_create=$(az group create --name $resourcegroup --location $location)
printf "Result of resource group create:\n $rg_create \n"

## Create Form recognizer resource
printf "${grn}CREATING THE FORM RECOGNIZER RESOURCE...${end}\n"
cognitiveServices=$(az cognitiveservices account create \
	--kind CognitiveServices --location $location --name $cognitiveservice --sku S0\
	-g $resourcegroup  --yes)
printf "Result of cognitive services create:\n $cognitiveServices \n"

# Create workspace through CLI
printf "${grn}Starting creation of AML workspace...${end}\n"
ws_result=$(az ml workspace create -n $workspacename -g $resourcegroup)
printf "Result of workspace create:\n $ws_result \n"
sleep 5

# Generate service principal credentials
printf "${grn}Generate service principal credentials...${end}\n"
credentials=$(az ad sp create-for-rbac --name "sp$resourcegroup" \
	--scopes /subscriptions/$sub_id/resourcegroups/$resourcegroup \
	--role Contributor)
#echo $credentials

## Retrieve key from cognitive services
printf "${grn}RETRIEVE KEY FOR COGNITIVE SERVICES...${end}\n"
cogKey=$(az cognitiveservices account keys list -g $resourcegroup --name $cognitiveservice --query "key1")
#
#
# Capture credentials for 'jq' parsing
sleep 5
credFile='cred.json'
printf "$credentials" > $credFile
clientID=$(cat $credFile | jq '.appId')
clientSecret=$(cat $credFile | jq '.password')
tenantID=$(cat $credFile | jq '.tenant')
rm $credFile

# Remove double-quotes
clientID=$(sed -e 's/^"//' -e 's/"$//' <<<"$clientID")
clientSecret=$(sed -e 's/^"//' -e 's/"$//' <<<"$clientSecret")
tenantID=$(sed -e 's/^"//' -e 's/"$//' <<<"$tenantID")
cogkey=$(sed -e 's/^"//' -e 's/"$//' <<<"$cogKey")

# Create variables file
printf "${grn}Writing out service principal variables...${end}\n"
env_variable_file='variables.env'
printf "AZURE_CLIENT_ID=$clientID \n" > $env_variable_file
printf "AZURE_CLIENT_SECRET=$clientSecret \n" >> $env_variable_file
printf "AZURE_TENANT_ID=$tenantID \n" >> $env_variable_file
printf "SUB_ID=$sub_id \n" >> $env_variable_file
printf "RESOURCE_GROUP=$resourcegroup \n" >> $env_variable_file
printf "WORKSPACE_NAME=$workspacename \n" >> $env_variable_file
printf "LOCATION=$location \n" >> $env_variable_file
printf "ENDPOINT=$endpoint \n" >> $env_variable_file
printf "COG_RESOURCE=$cognitiveservice \n" >> $env_variable_file
printf "COG_KEY=$cogkey \n" >> $env_variable_file
