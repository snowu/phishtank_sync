Build docker image from repo:

    From inside the repo folder using Dockerfile:

    docker build -t phishtank-api .
    docker run -p 8000:8000 phishtank-api

    Will instantiate a docker image on port 8000.

Download docker image:
    
    If you want to just download and run the image, you can find it here:

    https://hub.docker.com/repository/docker/snowu/phishtank-api/general

    or pull directly with docker

    sudo docker pull snowu/phishtank-api
    sudo docker run -p 8000:8000 snowu/phishtank-api


-------------------------------------------------------------------------------------------------------------------------------------------------------------------

*API Usage*

Download report:

    Report takes in JSON as parameters since to_time can be optional and having it in the url means using an additional url parameter like url_to_api/20240701?to_time=20240717
    It feels a bit wrong to do so since it's unintuitive that two values with the same logic and formatting use different way to integrate into API so i chose JSON for this

    Example curl will download report to report.json, from the first of July to the 17th. Date are accepted in iso8601 format, both dates format in the example are fine
    If timezone is not included, API will set timezone to UTC, since phishtank used UTC by default
    In addition, if a specific time is not passed, API will count the whole day of to_time, which is more intuitive. If i put 20240717, i expect results from the whole day as well.
    So, unless a time is specified (with T%H:%M:%S), the results will be from 00:00 of from_time to 23:59:59 of to_time

    It's also possible to pass timezone offsets, they will be converted to UTC, 

        so  "20240717T00:00:00-02:00" will be 2024-07-17 02:00:00

        and "20240717T00:00:00+02:00" will be 2024-07-16 22:00:00

    This is a tad counterintuitive until you realize that it counts as an offset from UTC,so +02 means a zone where it's 2 hours ahead of UTC which means to convert to UTC we move the clock back 2 hours.
    I suggest just passing dates and times without any timezone, as the API will convert and use UTC as basis
                                                                                    
    curl -o "report.json" -X "GET" --json '{"from_time": "20240701", "to_time": "2024-07-17"}' "http://localhost:8000/download_report"

Search domain:

    Pretty straightforward, API checks (case unsensitive) if {domain_to_search} is present in the url and returns a list of URLs that matched it. 
    In this case the argument is inline since it's just the one and it has to be present since FastAPI throws a 404 if the url is without {domain_to_search}

    curl -o "domain_search.json" -X "GET" "http://localhost:8000/search_domain/{domain_to_search}"
