import solaredge
from shellyapi.shellyapi import ShellyApi
import sys
import os
import datetime
import logging
from enum import Enum
import time


log = logging.getLogger("SolarManager")

class SolarStatus(Enum):
    NOT_CHARGED=1,
    ACTIVE_DAY=2,
    ACTIVE_NIGHT=3,

class BoilerStatus(Enum):
    UNDEF = 0
    ON=1,
    OFF=2


def main() -> int:
    logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

    SOLAR_EDGE_API_KEY = os.getenv('SOLAR_EDGE_API')
    SHELLY_API_KEY = os.getenv('SHELLY_CLOUD_API')
    
    site_id = 3415476
    shelly_url="https://shelly-63-eu.shelly.cloud"

    device = solaredge.Solaredge(SOLAR_EDGE_API_KEY)
    power_flow = device.get_current_power_flow(site_id)
    
    import_kw = power_flow['siteCurrentPowerFlow']['GRID']['currentPower']
    production_kw = power_flow['siteCurrentPowerFlow']['PV']['currentPower']
    consumtion_kw = power_flow['siteCurrentPowerFlow']['LOAD']['currentPower']

    print(f'import {import_kw}[kW]')
    print(f'consumtion {consumtion_kw}[kW]')
    print(f'pv production {production_kw}[kW]')

    shelly = ShellyApi(shelly_url, SHELLY_API_KEY)
    #device_id=shelly.get_device_ids()[0]
    #print(shelly.get_device_ids())
    device_id='ec6260822974'
    #print(shelly.plug_s_turn_on(channel = 0, device_id = device_id))
    do_enable_boiler= False
    boiler_consumtion_kw = 3.0 # concumption of 

    boiler_status_new=BoilerStatus.UNDEF
    boiler_status_old=BoilerStatus.UNDEF

    boiler_status_new=BoilerStatus.UNDEF
    boiler_status_old=BoilerStatus.UNDEF

    day_counter_min=0
    
    while True:
        if datetime.time(4,0) <= datetime.datetime.now().time()<= datetime.time(5,0) and (day_counter_min != 0):
            log.debug("reset boiler day counter")
            boiler_status_new=BoilerStatus.OFF
            shelly.plug_s_turn_off(channel = 0, device_id = device_id)
            day_counter_min = 0

        if day_counter_min < 180:

            device = solaredge.Solaredge(SOLAR_EDGE_API_KEY)
            power_flow = device.get_current_power_flow(site_id)
            
            import_kw = power_flow['siteCurrentPowerFlow']['GRID']['currentPower']
            production_kw = power_flow['siteCurrentPowerFlow']['PV']['currentPower']
            consumtion_kw = power_flow['siteCurrentPowerFlow']['LOAD']['currentPower']



            log.debug("Boiler not yet charged")
            if datetime.time(8,30) <= datetime.datetime.now().time() <= datetime.time(19,30):
                log.debug("Active day time")
                if production_kw > 3.5 and (import_kw + 0.5 <= 0):
                    boiler_status_new=BoilerStatus.ON
                    shelly.plug_s_turn_on(channel = 0, device_id = device_id)
                else:
                    boiler_status_new=BoilerStatus.OFF
                    shelly.plug_s_turn_off(channel = 0, device_id = device_id)

            elif datetime.time(1,00) <= datetime.datetime.now().time() <= datetime.time(4,00):
                log.debug("Active night time")
                boiler_status_new=BoilerStatus.ON
                shelly.plug_s_turn_on(channel = 0, device_id = device_id)
            else:
                boiler_status_new=BoilerStatus.OFF
                shelly.plug_s_turn_off(channel = 0, device_id = device_id)
                log.debug("Inactive time")

        if boiler_status_new != boiler_status_old:
            log.warning(f"New Boilder Status: {boiler_status_new}")
            boiler_status_old=boiler_status_new

        time.sleep(5)


    return 0

if __name__ == '__main__':
    sys.exit(main())

    