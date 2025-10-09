#!/bin/bash
# Get datadump and convert to ntriples
mkdir data/raw
cd data/raw
echo "Downloading the compressed knowledge graph assertions from the repository..."
curl -k -O https://zenodo.org/records/14605744/files/2025-01-05-rinf-xml-combined.nq.xz
echo "Uncompressing file into nquads..."
xz -d 2025-01-05-rinf-xml-combined.nq.xz
echo "Converting from nquads to ntriples... (this process takes a couple minutes)"
rev 2025-01-05-rinf-xml-combined.nq | cut -d "<" -f 2- |rev |sed 's/.$/./'  > 2025-01-05-rinf-xml-combined.nt
rm 2025-01-05-rinf-xml-combined.nq
cd ../..

# Subsets
echo "Subsetting and concatenating with the vocabularies into the benchmark knowledge graph subsets..."
sed -n 33538045,34761236p data/raw/2025-01-05-rinf-xml-combined.nt > data/raw/ES.nt
sed -n 35092900,46412047p data/raw/2025-01-05-rinf-xml-combined.nt > data/raw/FR.nt
# sed -n 50188479,50215374p data/raw/2025-01-05-rinf-xml-combined.nt > data/raw/LV.nt

# Create a single file for the knowledge graph subsets
for f in data/vocabularies/*.ttl; do (cat "${f}"; echo) >> data/vocabularies/vocabularies.ttl; done
cat data/vocabularies/vocabularies.ttl data/raw/2025-01-05-rinf-xml-combined.nt > data/ERA.ttl
cat data/vocabularies/vocabularies.ttl data/raw/ES.nt > data/ES.ttl
cat data/vocabularies/vocabularies.ttl data/raw/FR.nt > data/FR.ttl
# cat data/vocabularies/vocabularies.ttl data/raw/LV.nt > data/LV.ttl

# Free disk space
echo "Cleaning directories..."
rm -r data/raw

echo "Done."
