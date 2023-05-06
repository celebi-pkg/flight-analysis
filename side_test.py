from src.google_flight_analysis.scrape import _Scrape

sc = _Scrape()
sc._set_properties("RDU", "LGA", "2023-07-19", "2023-07-25")

url = sc._make_url()
results = sc._make_url_request(url)

#start_idx = results.index('Sort by:') + 1
#end_idx = [i for i in range(len(results)-1, start_idx, -1) if "more flights" in results[i]][0]

info = sc._get_info(results)

#print(info)
#sep_idx = [i-1 for i in range(len(info)) if info[i].strip() == '-']

groups = sc._partition_info(info)

print(groups)