Download report:

    Report takes in JSON since to_time can be Optional and having it in the url means using an additional url parameter like 
    url_to_api/20240701?to_time=20240717 and it feels a bit wrong to do so since it's unintuitive so i chose JSON for this

    Example curl will download report to report.json, from the first of July to the 17th. Date are accepted in iso8601 format, both dates in the example are fine
    If timezone is not included, we'll adapt since phishtank uses UTC by default

    curl -o "report.json" -X "GET" --json '{"from_time": "20240701", "to_time": "2024-07-17"}' "http://localhost:8000/download_report"

Search domain:

    Pretty straightforward, API checks if {domain_to_search} is present in the url and returns a list of URLs that matched it. 
    In this case the argument is inline since it's just the one and it has to be present and FastAPI throws a 404 if the url is without {domain_to_search}

    curl -o "domain_search.json" -X "GET" "http://localhost:8000/search_domain/{domain_to_search}"
