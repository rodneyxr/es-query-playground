#!/usr/bin/env python3

from elasticsearch import Elasticsearch
from jinja2 import Template

# Disable annoying warnings for development purposes
import warnings
warnings.filterwarnings("ignore")

es = Elasticsearch(
    ["https://localhost:9200"],
    http_auth=("elastic", "password"),
    verify_certs=False,
)

# Define the index name
index_name = "policy"

# Define the user's entitlements to be used in the query
user_entitlements = {
    "A",
    "B",
    "any/number/1",
    "any/number/2",
}

query_entitlements = {}
query_entitlements["all"] = []

for attr in user_entitlements:
    if attr.startswith("any/"):
        split_attr = attr.split("/")
        key = "any." + split_attr[1]
        query_entitlements.setdefault(key, []).append(attr)
    else:
        query_entitlements["all"].append(attr)

print("User Entitlements:", query_entitlements)

with open("query.json.j2", "r") as file:
    query_template = file.read()

template = Template(query_template)
query = template.render(
    entitlements=query_entitlements,
)

# Print the query
print("GET /policy/_search")
print(query)
print()

# Execute the query
response = es.search(index=index_name, body=query)

# Print the results
print("User Entitlements:", user_entitlements)
print()
print(f"Query Results ({response['hits']['total']['value']}):")
for hit in response["hits"]["hits"]:
    print(f"Document ID {hit['_id']}: {hit['_source']}")
