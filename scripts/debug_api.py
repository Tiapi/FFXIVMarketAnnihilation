"""
Quick debug script to inspect API structure
"""
from src.universalis_client import UniversalisClient

client = UniversalisClient()

# Get worlds
print("Getting worlds...")
worlds = client.get_worlds()
print(f"Total worlds: {len(worlds)}")
print("\nFirst 5 worlds:")
for world in worlds[:5]:
    print(world)

print("\n" + "="*60)

# Get datacenters
print("\nGetting datacenters...")
dcs = client.get_data_centers()
print(f"Total datacenters: {len(dcs)}")
print("\nDatacenters:")
for dc in dcs:
    print(dc)

# Find Chaos datacenter
print("\n" + "="*60)
print("\nSearching for Chaos datacenter...")
for dc in dcs:
    if 'Chaos' in str(dc):
        print(f"Found: {dc}")
