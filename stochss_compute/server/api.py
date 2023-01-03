import asyncio
import subprocess
from distributed import Client
from tornado.web import Application
from stochss_compute.server.is_cached import IsCachedHandler
from stochss_compute.server.run import RunHandler
from stochss_compute.server.sourceip import SourceIpHandler
from stochss_compute.server.status import StatusHandler
from stochss_compute.server.results import ResultsHandler
import os

def _make_app(dask_host, dask_scheduler_port, cache):
    scheduler_address = f'{dask_host}:{dask_scheduler_port}'
    return Application([
        (r"/api/v2/simulation/gillespy2/run", RunHandler, {'scheduler_address': scheduler_address, 'cache_dir': cache}),
        (r"/api/v2/simulation/gillespy2/(?P<results_id>.*?)/(?P<n_traj>[1-9]\d*?)/status", StatusHandler, {'scheduler_address': scheduler_address, 'cache_dir': cache}),
        (r"/api/v2/simulation/gillespy2/(?P<results_id>.*?)/(?P<n_traj>[1-9]\d*?)/results", ResultsHandler, {'cache_dir': cache}),
        (r"/api/v2/cache/gillespy2/(?P<results_id>.*?)/(?P<n_traj>[1-9]\d*?)/is_cached", IsCachedHandler, {'cache_dir': cache}),
        (r"/api/v2/cloud/sourceip", SourceIpHandler),
    ])

async def start_api(
        port = 29681, 
        cache = 'cache/',
        dask_host = 'localhost',
        dask_scheduler_port = 8786,
        rm_cache_on_exit = False,
        ):
    
    """
    Start the REST API with the following arguments.

    :param port: The port to listen on.
    :type port: int

    :param cache: The cache directory path.
    :type cache: str

    :param dask_host: The address of the dask cluster.
    :type dask_host: str

    :param dask_scheduler_port: The port of the dask cluster.
    :type dask_scheduler_port: int

    :param rm_cache_on_exit: Delete the cache when exiting this program.
    :type rm_cache_on_exit: bool
    """
    
    cache_path = os.path.abspath(cache)
        
    app = _make_app(dask_host, dask_scheduler_port, cache)
    app.listen(port)
    print(f'StochSS-Compute listening on: :{port}')
    print(f'Cache directory: {cache_path}')
    print(f'Connecting to Dask scheduler at: {dask_host}:{dask_scheduler_port}\n')
    try:
        await asyncio.Event().wait()
    finally:
        print('Shutting down.')
        if rm_cache_on_exit and os.path.exists(cache_path):
            print('Removing cache...', end='')
            subprocess.Popen(['rm', '-r', cache_path])
        client = Client(f'{dask_host}:{dask_scheduler_port}')
        print('Canceling jobs...', end='')
        await client.cancel()
        print('OK')
        print('Closing Workers...', end='')
        await client.retire_workers(close_workers=True)
        print('OK')
        print('Shutting down cluster...', end='')
        await client.cluster.close()
        print('OK')
        print('Closing client...', end='')
        await client.close()
        print('OK')
    
    

