import argparse
import requests

API_BASE_URL = "https://otx.alienvault.com/"


class OTXClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-OTX-API-KEY": api_key})

    def fetch_urls(self, domain, include_subdomains=False):
        page = 1
        while True:
            url = self._format_url(domain, page, include_subdomains)
            response = self.session.get(url)

            if response.status_code == 200:
                result = response.json()
                if "url_list" in result:
                    for entry in result["url_list"]:
                        url_key = self._get_url_key(entry)
                        if url_key:
                            yield entry[url_key]

                    if not result["has_next"]:
                        break

                    page += 1
                else:
                    print(f"No associated URLs found for the domain: {domain}")
                    break
            elif response.status_code == 504:
                print("Timeout occurred. Skipping to the next domain...")
                break
            else:
                response.raise_for_status()

    def _format_url(self, domain, page, include_subdomains):
        base_url = f"{API_BASE_URL}api/v1/indicators/domain/{domain}/url_list"
        if include_subdomains:
            url = f"{base_url}?limit=100&page={page}&include_subdomains=true"
        else:
            url = f"{base_url}?limit=100&page={page}"
        return url

    def _get_url_key(self, entry):
        keys = ["URL", "url", "Url"]
        for key in keys:
            if key in entry:
                return key
        return None


def process_domains(domains, include_subdomains):
    client = OTXClient(API_KEY)
    for domain in domains:
        print(f"Fetching URLs for domain: {domain}")
        urls = client.fetch_urls(domain, include_subdomains)
        url_list = list(urls)
        if url_list:
            output_file = f"{domain}.txt"
            with open(output_file, "a") as file:
                file.write("\n".join(url_list) + "\n")
            print(f"URLs saved for domain: {domain}")
        else:
            print(f"No associated URLs found for the domain: {domain}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alienvault OTX URL Spider")
    parser.add_argument("-d", "--domain", help="Single domain to fetch URLs for")
    parser.add_argument("-subs", "--include_subdomains", action="store_true", help="Include subdomains")
    args = parser.parse_args()

    API_KEY = "YOUR API KEY"

    if not args.domain:
        parser.error("A domain must be provided.")

    domains = [args.domain]

    process_domains(domains, args.include_subdomains)
