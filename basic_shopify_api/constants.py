# Valid API version in URL path: YYYY-MM or unstable
VERSION_PATTERN = r"([0-9]{4}-[0-9]{2})|unstable"
# /oauth/authorize, /oauth/access_token do not require authentication
NOT_AUTHABLE_PATTERN = r"\/oauth\/(authorize|access_token)"
# /oauth/access_scopes does not require versioned API path
NOT_VERSIONABLE_PATTERN = r"\/(oauth\/access_scopes)"
# For extracting next/prev link header on REST API calls
LINK_PATTERN = r"<.*page_info=([a-zA-Z0-9\-_]+).*>; rel=\"(next|previous)\""
# Header supplied by Shopify when rate limit is hit
RETRY_HEADER = "retry-after"
# Header supplied by Shopify for REST API calls, used by LINK_PATTERN
LINK_HEADER = "link"
# Header to send for public API calls
ACCESS_TOKEN_HEADER = "x-shopify-access-token"
# Default API version
DEFAULT_VERSION = "2020-04"
# Default API mode
DEFAULT_MODE = "public"
# Alternate API mode
ALT_MODE = "private"
# One second in milliseconds
ONE_SECOND = 1000
# REST API type
REST = "rest"
# GraphQL API type
GRAPHQL = "graphql"
