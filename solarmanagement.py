import solaredge
import sys
import os

def main() -> int:

    API_KEY = os.getenv('SOLAR_EDGE_API')
    site_id = 3415476

    device = solaredge.Solaredge(API_KEY)
    power_flow = device.get_current_power_flow(site_id)
    
    import_kw = power_flow['siteCurrentPowerFlow']['GRID']['currentPower']
    production_kw = power_flow['siteCurrentPowerFlow']['PV']['currentPower']
    consumtion_kw = power_flow['siteCurrentPowerFlow']['LOAD']['currentPower']

    print(f'import {import_kw}[kW]')
    print(f'consumtion {consumtion_kw}[kW]')
    print(f'pv production {production_kw}[kW]')


    return 0

if __name__ == '__main__':
    sys.exit(main()) 