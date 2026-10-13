# Retrieval contract

Target: UCI Wine id109 and Iris id53 classification tables. Scope: every row and feature in the selected original table versions, plus their official dictionaries. Access date: 2026-10-13.

Expected counts from official landing pages: Wine 178 rows/13 features; Iris 150 rows/4 features. Labels retained. No sample, class, time, geography or feature filters within the selected tables. No pagination is needed for these small static original files. Server-side selection is by dataset id; local archive member selection will retain wine.data/wine.names and iris.data/iris.names. Preserve original row order and source bytes. The Iris selected version is iris.data; known differences from the Fisher article will be documented, not silently corrected.

Candidates compared: official UCI static archives; official UCI package-mediated fetch; third-party/bundled copies. Official static archives expose the original text tables and dictionaries with DOI/CC BY metadata, incur about 10 kB for the two entire archives, and need no new client dependency or login. Package fetching is legitimate but unnecessary here. Bundled/third-party files add no scientific coverage and can differ in historical Iris corrections; excluded from research inputs. Wine Quality is a different dataset and is not substituted for Wine.

Authorities: https://archive.ics.uci.edu/dataset/109/winedataset and https://archive.ics.uci.edu/dataset/53/iris. Official download links are selected from these pages. Two initial web opens timed out; opening search-resolved official pages succeeded, without changing the target data or stopping for a user.

Count reconciliation will be from full local parsing. Expected source SHA256 is not published on these pages; measured local hashes prove file identity and subsequent change detection, not independent publisher checksum authentication. Confirm ZIP CRC and parse actual schema/rows. Normal browser/search traffic is not measured by the local data-transfer tool; the bounded archive downloads themselves are measured. No credentials are required.
