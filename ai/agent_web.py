!adk create sample-agent --model gemini-2.5-flash-lite --api_key $GOOGLE_API_KEY
url_prefix = get_adk_proxy_url()
!adk web --url_prefix {url_prefix}
