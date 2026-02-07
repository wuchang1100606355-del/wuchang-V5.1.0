import urllib.request

def make_tiny(url):
    api_url = "http://tinyurl.com/api-create.php?url=" + url
    try:
        with urllib.request.urlopen(api_url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

long_url = "https://statewide-breach-extreme-diabetes.trycloudflare.com/enroll_agent.py"
short_url = make_tiny(long_url)
print(f"Short URL: {short_url}")
