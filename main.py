from observations.collection_service import CollectionService

import time

collection_service = CollectionService()

while True:

    observation = collection_service.collect_and_store()

    print(
        f"✔ Observation collected | "
        f"Battery: {observation.battery_percentage}% | "
        f"CPU: {observation.cpu_usage}% | "
        f"RAM: {observation.ram_usage}%"
    )

    time.sleep(300)