# BAE NGSI Query Extension

BAE extension for the monetization of NGSI Queries using a FIWARE Keyrock as IDM.

This extension requires the following parameters to be provided during product purchase:

- **Application ID**: Client ID of the application created by the seller in Keyrock.
- **Acquisition Role**: Name of the role that will be created within the seller's application. The extension will add the text ".plugin" to distinguish it from other roles. The extension will check for the role (+ .plugin) in the Keyrock application and will create it if not present. The role will be assigned to the customer during product purchase.
- **Permission Name**: Name of the permission that will be created within the seller's application.
- **Action**: HTTP method used by the customer to manipulate the resources sold by the product.
- **Resource**: Path where the resources are located. It follows the same format of the NGSI v2 RESTful API.
- **Is regex?**: Indicates if the resources have been specified using a regular expression.

Once the product is acquired, the customer will be granted the new role and permission in the Keyrock application.

## Configuration

To work properly, this extension requires the following environment variables to have been configured in the BAE Charging Backend component:

* **BAE_ASSET_IDM_USER**: Admin user (email) used to access Keyrock APIs
* **BAE_ASSET_IDM_PASSWORD**: Password of admin user used to access Keyrock APIs
* **BAE_ASSET_IDM_URL**: URL of the Keyrock instance

## Installation

It is assumed that BAE instance has been installed using dockers.

1. Package the extension in a zip file

    `$ zip ngsi-query.zip keyrock_client.py ngsi_query.py package.json`

2. Copy zip file to charging-plugins directory of BAE instance

    `$ sudo cp ngsi-query.zip ~/fiware-bae/charging-plugins/`

3. Get into the shell of the Docker container of the BAE Charging Backend component

    `$ docker exec -i -t fiware-bae_charging_1 bash`

4. Load the extension in BAE

    `# ./manage.py loadplugin plugins/ngsi-query.zip`

5. (Optional) Check the extension has been loaded correctly

    `# ./manage.py listplugins`

## Notes

This extension has been created based on the BAE NGSI-LD Query Extension.

`$ git clone --branch i4trust https://github.com/Ficodes/bae-ngsild-query.git`
