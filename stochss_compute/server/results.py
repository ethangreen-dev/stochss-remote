'''
stochss_compute.server.results
'''
from datetime import datetime
from tornado.web import RequestHandler
from stochss_compute.core.errors import RemoteSimulationError
from stochss_compute.core.messages import ResultsResponse
from stochss_compute.server.cache import Cache

class ResultsHandler(RequestHandler):
    '''
    Endpoint for Results objects.
    '''

    def initialize(self, cache_dir):
        '''
        Set the cache directory.
        '''
        self.cache_dir = cache_dir

    async def get(self, results_id = None, n_traj = None):
        '''
        Process GET request.

        :param results_id: Hash of the simulation.
        :param n_traj: Number of trajectories in the request.
        '''
        if None in (results_id, n_traj):
            raise RemoteSimulationError(f'Malformed request | <{self.request.remote_ip}>')
        n_traj = int(n_traj)
        print(f'{datetime.now()} | <{self.request.remote_ip}> | Results Request | <{results_id}>')
        cache = Cache(self.cache_dir, results_id)
        if cache.is_ready(n_traj):
            results = cache.read()
            results_response = ResultsResponse(results)
            self.write(results_response.encode())
        else:
            # This should not happen!
            self.set_status(404, f'Results "{results_id}" not found.')
        self.finish()
