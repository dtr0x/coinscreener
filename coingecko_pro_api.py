import pycoingecko, json

CG_API_URL_BASE = 'https://pro-api.coingecko.com/api/v3/'
CG_API_KEY = '<YOUR API KEY>'

class CoinGeckoAPI(pycoingecko.CoinGeckoAPI):
    def __init__(self):
        super().__init__(api_base_url=CG_API_URL_BASE)

    def __request(self, url):
        headers = {'X-Cg-Pro-Api-Key': CG_API_KEY}
        try:
            response = self.session.get(url, headers=headers, timeout=self.request_timeout)
        except requests.exceptions.RequestException:
            raise

        try:
            response.raise_for_status()
            content = json.loads(response.content.decode('utf-8'))
            return content
        except Exception as e:
            # check if json (with error message) is returned
            try:
                content = json.loads(response.content.decode('utf-8'))
                raise ValueError(content)
            # if no json
            except json.decoder.JSONDecodeError:
                pass

            raise
