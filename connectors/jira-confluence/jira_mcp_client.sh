#!/bin/bash

# Jira/Confluence MCP Client
# This script provides a simple interface to connect to Jira and Confluence

# Load environment variables from .env file
ENV_FILE="${HOME}/.junie/.env/jira_confluence.env"
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo "Error: Environment file not found at $ENV_FILE"
    echo "Please create the file with the following variables:"
    echo "JIRA_API_KEY, JIRA_DOMAIN, CONFLUENCE_DOMAIN, JIRA_USER_EMAIL"
    exit 1
fi

# Configuration
API_KEY="${JIRA_API_KEY}"
if [ -z "$API_KEY" ]; then
    echo "Error: JIRA_API_KEY environment variable not set"
    exit 1
fi

# Atlassian domain configuration
JIRA_DOMAIN="${JIRA_DOMAIN:-your-domain.atlassian.net}"
CONFLUENCE_DOMAIN="${CONFLUENCE_DOMAIN:-your-domain.atlassian.net}"

# Base URLs
JIRA_BASE_URL="https://$JIRA_DOMAIN"
CONFLUENCE_BASE_URL="https://$CONFLUENCE_DOMAIN"

# User email for authentication
USER_EMAIL="${JIRA_USER_EMAIL}"
if [ -z "$USER_EMAIL" ]; then
    echo "Error: JIRA_USER_EMAIL environment variable not set"
    exit 1
fi

# Headers for API requests
# For Atlassian Cloud, use Basic auth with email and API token
# Encode the credentials as base64: "email:api_token"
AUTH_CREDENTIALS=$(echo -n "$USER_EMAIL:$API_KEY" | base64)
AUTH_HEADER="Authorization: Basic $AUTH_CREDENTIALS"
CONTENT_HEADER="Content-Type: application/json"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test connection to Jira
test_jira_connection() {
    echo -e "${BLUE}Testing connection to Jira...${NC}"

    echo -e "${BLUE}Request URL: $JIRA_BASE_URL/rest/api/3/myself${NC}"
    echo -e "${BLUE}Headers: $AUTH_HEADER, $CONTENT_HEADER${NC}"

    # Use -v for verbose output but redirect stderr to a variable
    exec 3>&1
    verbose_output=$(curl -v -s -w "%{http_code}" -X GET \
        -H "$AUTH_HEADER" \
        -H "$CONTENT_HEADER" \
        "$JIRA_BASE_URL/rest/api/3/myself" 2>&1 1>&3)
    exec 3>&-

    # Store the response and status code
    response=$(curl -s -w "%{http_code}" -X GET \
        -H "$AUTH_HEADER" \
        -H "$CONTENT_HEADER" \
        "$JIRA_BASE_URL/rest/api/3/myself")

    http_code=${response: -3}
    response_body=${response:0:${#response}-3}

    if [ "$http_code" -eq 200 ]; then
        display_name=$(echo "$response_body" | grep -o '"displayName":"[^"]*' | cut -d'"' -f4)
        echo -e "${GREEN}✅ Successfully connected to Jira as: $display_name${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to connect to Jira. Status code: $http_code${NC}"
        echo -e "${RED}Response: $response_body${NC}"
        echo -e "${RED}Verbose debug information:${NC}"
        echo -e "${RED}$verbose_output${NC}"

        # Add user information for debugging
        echo -e "${BLUE}Using email: $USER_EMAIL${NC}"
        return 1
    fi
}

# Function to get a Jira issue
get_jira_issue() {
    local issue_key=$1

    if [ -z "$issue_key" ]; then
        echo -e "${RED}Error: Issue key is required${NC}"
        return 1
    fi

    echo -e "${BLUE}Fetching Jira issue: $issue_key${NC}"

    response=$(curl -s -w "%{http_code}" -X GET \
        -H "$AUTH_HEADER" \
        -H "$CONTENT_HEADER" \
        "$JIRA_BASE_URL/rest/api/3/issue/$issue_key")

    http_code=${response: -3}
    response_body=${response:0:${#response}-3}

    if [ "$http_code" -eq 200 ]; then
        # Extract key information from the JSON response
        summary=$(echo "$response_body" | grep -o '"summary":"[^"]*' | head -1 | cut -d'"' -f4)
        status=$(echo "$response_body" | grep -o '"status":{[^}]*"name":"[^"]*' | grep -o '"name":"[^"]*' | cut -d'"' -f4)

        echo -e "${GREEN}Issue Summary: $summary${NC}"
        echo -e "${GREEN}Status: $status${NC}"

        # Save the full response to a file for further processing
        echo "$response_body" > "issue_${issue_key}.json"
        echo -e "${GREEN}Full response saved to issue_${issue_key}.json${NC}"

        return 0
    else
        echo -e "${RED}❌ Failed to get issue $issue_key. Status code: $http_code${NC}"
        echo -e "${RED}Response: $response_body${NC}"
        return 1
    fi
}

# Function to search for Jira issues
search_jira_issues() {
    local jql_query=$1

    if [ -z "$jql_query" ]; then
        jql_query="created >= -30d ORDER BY created DESC"
    fi

    echo -e "${BLUE}Searching for Jira issues with query: $jql_query${NC}"

    response=$(curl -s -w "%{http_code}" -X POST \
        -H "$AUTH_HEADER" \
        -H "$CONTENT_HEADER" \
        -d "{\"jql\":\"$jql_query\",\"maxResults\":10}" \
        "$JIRA_BASE_URL/rest/api/3/search")

    http_code=${response: -3}
    response_body=${response:0:${#response}-3}

    if [ "$http_code" -eq 200 ]; then
        # Save the response to a file
        echo "$response_body" > "jira_search_results.json"

        # Extract and display issue keys and summaries
        echo -e "${GREEN}Search results:${NC}"
        issue_count=$(echo "$response_body" | grep -o '"total":[0-9]*' | cut -d':' -f2)
        echo -e "${GREEN}Found $issue_count issues. Showing first 10:${NC}"

        # This is a simple extraction that might not work for all JSON structures
        # A proper JSON parser would be better
        keys=$(echo "$response_body" | grep -o '"key":"[^"]*' | cut -d'"' -f4)
        summaries=$(echo "$response_body" | grep -o '"summary":"[^"]*' | cut -d'"' -f4)

        # Print results
        paste <(echo "$keys") <(echo "$summaries") | while read -r key summary; do
            echo -e "${GREEN}- $key: $summary${NC}"
        done

        echo -e "${GREEN}Full response saved to jira_search_results.json${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to search issues. Status code: $http_code${NC}"
        echo -e "${RED}Response: $response_body${NC}"
        return 1
    fi
}

# Function to get a Confluence page
get_confluence_page() {
    local page_id=$1

    if [ -z "$page_id" ]; then
        echo -e "${RED}Error: Page ID is required${NC}"
        return 1
    fi

    echo -e "${BLUE}Fetching Confluence page: $page_id${NC}"

    response=$(curl -s -w "%{http_code}" -X GET \
        -H "$AUTH_HEADER" \
        -H "$CONTENT_HEADER" \
        "$CONFLUENCE_BASE_URL/wiki/rest/api/content/$page_id?expand=body.storage")

    http_code=${response: -3}
    response_body=${response:0:${#response}-3}

    if [ "$http_code" -eq 200 ]; then
        # Extract key information
        title=$(echo "$response_body" | grep -o '"title":"[^"]*' | head -1 | cut -d'"' -f4)

        echo -e "${GREEN}Page Title: $title${NC}"

        # Save the full response to a file
        echo "$response_body" > "confluence_page_${page_id}.json"
        echo -e "${GREEN}Full response saved to confluence_page_${page_id}.json${NC}"

        return 0
    else
        echo -e "${RED}❌ Failed to get Confluence page $page_id. Status code: $http_code${NC}"
        echo -e "${RED}Response: $response_body${NC}"
        return 1
    fi
}

# Function to search Confluence
search_confluence() {
    local query=$1

    if [ -z "$query" ]; then
        echo -e "${RED}Error: Search query is required${NC}"
        return 1
    fi

    echo -e "${BLUE}Searching Confluence for: $query${NC}"

    response=$(curl -s -w "%{http_code}" -X GET \
        -H "$AUTH_HEADER" \
        -H "$CONTENT_HEADER" \
        "$CONFLUENCE_BASE_URL/wiki/rest/api/content/search?cql=text~\"$query\"&limit=10")

    http_code=${response: -3}
    response_body=${response:0:${#response}-3}

    if [ "$http_code" -eq 200 ]; then
        # Save the response to a file
        echo "$response_body" > "confluence_search_results.json"

        # Extract and display page titles and IDs
        echo -e "${GREEN}Search results:${NC}"
        result_count=$(echo "$response_body" | grep -o '"size":[0-9]*' | head -1 | cut -d':' -f2)
        echo -e "${GREEN}Found $result_count pages. Showing first 10:${NC}"

        # Extract titles and IDs
        titles=$(echo "$response_body" | grep -o '"title":"[^"]*' | cut -d'"' -f4)
        ids=$(echo "$response_body" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

        # Print results
        paste <(echo "$ids") <(echo "$titles") | while read -r id title; do
            echo -e "${GREEN}- $id: $title${NC}"
        done

        echo -e "${GREEN}Full response saved to confluence_search_results.json${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to search Confluence. Status code: $http_code${NC}"
        echo -e "${RED}Response: $response_body${NC}"
        return 1
    fi
}

# Function to display help
show_help() {
    echo "Jira/Confluence MCP Client"
    echo "Usage: $0 [command] [arguments]"
    echo ""
    echo "Commands:"
    echo "  test                   Test connection to Jira"
    echo "  issue [ISSUE_KEY]      Get details of a Jira issue"
    echo "  search [JQL_QUERY]     Search for Jira issues (default: recent issues)"
    echo "  page [PAGE_ID]         Get a Confluence page"
    echo "  find [QUERY]           Search Confluence"
    echo "  help                   Show this help message"
    echo ""
    echo "Before using this script, make sure to set your Jira/Confluence credentials in the environment file:"
    echo "${HOME}/.junie/.env/jira_confluence.env"
}

# Main function - Protected implementation
# This function is protected and should only be called from this script
# It handles the core functionality of the connector
protected_main() {
    # Check if domain is configured
    if [ "$JIRA_DOMAIN" = "your-domain.atlassian.net" ]; then
        echo -e "${RED}Error: You need to configure your Atlassian domain in the environment file${NC}"
        echo -e "${RED}Edit ${HOME}/.junie/.env/jira_confluence.env and set JIRA_DOMAIN and CONFLUENCE_DOMAIN variables${NC}"
        return 1
    fi

    # Process command line arguments
    local command=$1
    shift

    case "$command" in
        "test")
            test_jira_connection
            ;;
        "issue")
            get_jira_issue "$1"
            ;;
        "search")
            search_jira_issues "$1"
            ;;
        "page")
            get_confluence_page "$1"
            ;;
        "find")
            search_confluence "$1"
            ;;
        "help"|"")
            show_help
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            show_help
            return 1
            ;;
    esac
}

# Public interface function
# This function serves as the entry point for the script
main() {
    # Check if the script is being sourced
    if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
        echo -e "${RED}Error: This script should not be sourced${NC}"
        return 1
    fi
    
    # Check for required permissions
    if [[ ! -x "${BASH_SOURCE[0]}" ]]; then
        echo -e "${RED}Error: Script must be executable. Run: chmod +x ${BASH_SOURCE[0]}${NC}"
        return 1
    fi
    
    # Call the protected implementation
    protected_main "$@"
}

# Run the main function with all arguments
main "$@"
