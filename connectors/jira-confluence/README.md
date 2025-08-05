# Jira/Confluence Connector

This connector provides a simple interface to connect to Jira and Confluence APIs using a shell script.

## Setup

1. Create an environment file at `../.env/jDEV.env` with the following variables:
   ```
   JIRA_API_KEY="your-api-key"
   JIRA_DOMAIN="your-domain.atlassian.net"
   CONFLUENCE_DOMAIN="your-domain.atlassian.net"
   JIRA_USER_EMAIL="your-email@example.com"
   ```

2. Make the script executable:
   ```
   chmod +x jira_mcp_client.sh
   ```

## Usage

### Test Connection
```
./jira_mcp_client.sh test
```

### Get Jira Issue
```
./jira_mcp_client.sh issue ISSUE-123
```

### Search Jira Issues
```
./jira_mcp_client.sh search "project = XYZ AND status = Open"
```

### Get Confluence Page
```
./jira_mcp_client.sh page PAGE_ID
```

### Search Confluence
```
./jira_mcp_client.sh find "search term"
```

## Security Considerations

- The environment file contains sensitive information and should be protected with appropriate file permissions:
  ```
  chmod 600 ~/.junie/.env/jira_confluence.env
  ```
- Consider using a credential manager or secret storage service for production environments
- Implement a regular key rotation policy to minimize the impact of potential key exposure

## References

- [Atlassian Cloud REST API Authentication](https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/)
- [Jira Cloud REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)
- [Confluence Cloud REST API Documentation](https://developer.atlassian.com/cloud/confluence/rest/)
