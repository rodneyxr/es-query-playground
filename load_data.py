#!/usr/bin/env python3

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from pprint import pprint

# Disable annoying warnings for development purposes
import warnings
warnings.filterwarnings("ignore")

# Connect to Elasticsearch
es = Elasticsearch(
    ["https://localhost:9200"],
    http_auth=("elastic", "password"),
    verify_certs=False
    )

# Define the index name
index_name = "policy"

policies = [
    [],
    ["A"],
    ["B"],
    ["A", "B"],
    ["any/number/1"],
    ["any/number/2"],
    ["any/number/3"],
    ["any/number/1", "any/number/2"],
    ["any/rainbow/red"],
    ["any/rainbow/orange"],
    ["any/rainbow/yellow"],
    ["any/rainbow/red", "any/rainbow/orange"],
    ["any/rainbow/red", "any/rainbow/orange", "any/rainbow/yellow"],
    ["A", "any/number/1"],
    ["B", "any/number/2"],
    ["A", "B", "any/number/1"],
    ["A", "B", "any/rainbow/yellow"],
    ["A", "B", "any/number/1", "any/number/2", "any/rainbow/red", "any/rainbow/orange", "any/rainbow/yellow"],
    ["SHOULD_NEVER_SHOW"],
]

documents = []
for i, policy in enumerate(policies):

    es_policy = {}

    for attr in policy:
        if attr.startswith("any/"):
            split_attr = attr.split("/")
            key = "any." + split_attr[1]
            es_policy.setdefault(key, []).append(attr)
        else:
            es_policy.setdefault("all", []).append(attr)

    documents.append(
        {
            "_index": index_name,
            "_id": i,
            "_source": {
                "policy": es_policy
            }
        }
    )
    print(f"Document {i}:")
    pprint(es_policy)
    print()

# Check if the index exists, and delete if it does
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

# Create the index
es.indices.create(index=index_name)

# Bulk load the documents into Elasticsearch
bulk(es, documents)

print("Sample data loaded into Elasticsearch.")
