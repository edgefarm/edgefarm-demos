import os
import signal
import asyncio
import logging

import edgefarm_application as ef
from seat_res_train_monitor import TrainStatusCollector
from seat_info_proxy_monitor import SeatInfoProxyMonitor
from seat_res_ads_state_reporter import SeatResAdsStateReporter
from ads_event_reporter import AdsEventReporter


async def main():
    loop = asyncio.get_event_loop()

    # Initialize EdgeFarm SDK
    if os.getenv("IOTEDGE_MODULEID") is not None:
        await ef.application_module_init_from_environment(loop)
    else:
        print("Warning: Running example outside IOTEDGE environment")
        await ef.application_module_init(
            loop, "SeatRes", "fleet-seat-info-monitor", "no-runtime-id"
        )

    # Create a queue that we will use to store events.
    event_q = asyncio.Queue()

    seat_res_train_monitor = TrainStatusCollector(event_q)
    await seat_res_train_monitor.start()

    seat_info_proxy_monitor = SeatInfoProxyMonitor(event_q)

    seat_res_ads_state_reporter = SeatResAdsStateReporter(
        event_q, seat_res_train_monitor.trains, seat_info_proxy_monitor.state
    )
    event_reporter = AdsEventReporter()

    def signal_handler():
        event_q.put_nowait("stop")

    for sig in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(getattr(signal, sig), signal_handler)

    while True:
        event = await event_q.get()
        print(f"main loop: event {event}")
        if type(event) is str and event == "stop":
            break
        else:
            await event_reporter.report(event)

    print("Shutting down...")
    seat_res_ads_state_reporter.stop()
    await seat_res_train_monitor.stop()
    await ef.application_module_term()


if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "INFO").upper(),
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    asyncio.run(main())
