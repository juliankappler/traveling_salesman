
import requests
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

'''
This file contains the definitions of the following three classes

openroute_requests: 
    This class methods to interact with the openrouteservice.org API, i.e. to
    search locations, as well as get distances and directions between those
    locations

genetic_algorithm:
    This class implements a genetic algorithm to solve the traveling salesman
    problem for a round trip (i.e. the agent ending at the same location where
    it started, while visiting each of the other locations only once)

traveling_salesman:
    This class takes a list of location names, uses the openroute_requests
    class to resolve them and obtain the distances between them, and then 
    uses the genetic_algorithm class to solve the traveling salesman problem
    for the given location names


To Do: add documentation to all classes!

'''

class openroute_requests():
    '''
    This class methods to interact with the openrouteservice.org API, i.e. to
    search locations, as well as get distances and directions between those
    locations
    '''

    def __init__(self,parameters):
        #
        self.set_default_parameters()
        #
        self.set_parameters(parameters=parameters)
        
    def set_default_parameters(self):
        self.verbose = False
        self.api_key = 'not set'
        self.mode_of_transportation = 'driving-car'
        self.set_openrouteservice_api_urls()
        # 
        # see https://openrouteservice.org/dev/#/api-docs/v2/directions/{profile}/get
        self.allowed_modes_of_transportation = ['cycling-electric',
                                        'cycling-mountain',
                                        'cycling-regular',
                                        'cycling-road',
                                        'driving-car',
                                        'driving-hgv',
                                        'foot-hiking',
                                        'foot-walking',
                                        'foot-wheelchair']
        
    def set_openrouteservice_api_urls(self):
        self.requests_url_matrix = ('https://api.openrouteservice.org/'
                     'v2/matrix/{0}'.format(self.mode_of_transportation))
        self.requests_url_directions = ('https://api.openrouteservice.org/'
                    'v2/directions/{0}'.format(self.mode_of_transportation))

    def set_parameters(self,parameters):

        try:
            self.api_key = parameters['api_key']
        except KeyError:
            pass
        
        try:
            self.requests_url = parameters['requests_url']
        except KeyError:
            pass
        
        try:
            self.verbose = parameters['verbose']
        except KeyError:
            pass

        try:
            self.mode_of_transportation = parameters['mode_of_transportation']
            if self.mode_of_transportation \
                    not in self.allowed_modes_of_transportation:
                error_msg = ("Provided mode of transportation {0} not "
                             "in list of known modes of transportation: {1}")
                raise RuntimeError(
                                error_msg.format(
                                        self.mode_of_transportation,
                                        self.allowed_modes_of_transportation,
                                                )
                                    )
        except KeyError:
            pass
        
        if self.api_key == 'not set':
            print("Warning: api_key is not set!")

        self.set_openrouteservice_api_urls()

    def get_location(self,name):
        #
        request_link = ('https://api.openrouteservice.org/geocode/search?'
            'api_key={0}&text={1}'.format(self.api_key,
                                        name.replace(' ','%20')))
        #
        accept_string = ('application/json, application/geo+json, '
                         'application/gpx+xml, img/png; charset=utf-8')
        headers = {
            'Accept': accept_string,
        }
        call = requests.get(request_link,
                            headers=headers)
        #
        call_json = call.json()
        label = call_json['features'][0]['properties']['label']
        coordinates = call_json['features'][0]['geometry']['coordinates']
        #
        return label, coordinates        
        
    def get_distance_matrix(self,locations):
        #
        body = {
                "locations":locations,
                "metrics":["distance","duration"],
                "resolve_locations":"true",
                "units":"km"
               }
        accept_string = ('application/json, application/geo+json, '
                         'application/gpx+xml, img/png; charset=utf-8')
        headers = {
            'Accept': accept_string,
            'Authorization': self.api_key,
            'Content-Type': 'application/json; charset=utf-8'
        }
        call = requests.post(self.requests_url_matrix, 
                             json=body, headers=headers)
        if self.verbose:
            print('status code = {0} {1}'.format(call.status_code,
                                                call.reason))
        distances = call.json()
        distance_matrix = np.array(distances['distances'])
        #
        if (distance_matrix == None).any():
            if self.verbose:
                print("Could not resolve the following distances:")
                for e in zip(*np.where(distance_matrix==None)):
                    print('From location {0} to location {1}'.format(*e))
            error_msg = ("Could not determine the distances between {0} of "
                         "the {1} given location pairs")
            raise RuntimeError(error_msg.format(
                                np.sum(distance_matrix == None),
                                len(locations)**2
                                ))
        #
        return distance_matrix

    def get_trajectory_segments_for_two_locations(self,location1,location2):
        #
        accept_string = ('application/json, application/geo+json, '
                         'application/gpx+xml, img/png; charset=utf-8')
        headers = {
        'Accept': accept_string,
        }
        #
        current_request = ('?api_key={api_key}&start={start_x},{start_y}'
                        '&end={end_x},{end_y}')
        current_request = current_request.format(
                    api_key=self.api_key,
                    start_x=location1[0],start_y=location1[1],
                    end_x=location2[0],end_y=location2[1])
        current_request = self.requests_url_directions + current_request
        call = requests.get(current_request, headers=headers)
        #
        if self.verbose:
            print('status code = {0} {1}'.format(call.status_code,
                                                call.reason))
        #
        current_trajectory_data = call.json()
        try:
            current_trajectory = \
            current_trajectory_data['features'][0]['geometry']['coordinates']
        except KeyError:
            raise RuntimeError("Did not receive proper trajectory segment.\n"\
                        + "Status code of api call: {0} {1}".format(
                                                call.status_code,call.reason))
        current_trajectory = np.array(current_trajectory)
        return current_trajectory

    def get_trajectory_segments(self,locations):
        #
        trajectory_segments = []
        #
        for i,e in enumerate(locations[:-1]):
            trajectory_segments.append(\
                self.get_trajectory_segments_for_two_locations(e,
                                                        locations[i+1]) )
        #
        return trajectory_segments
    


class genetic_algorithm():
    '''
    This class implements a genetic algorithm to solve the traveling salesman
    problem for a round trip (i.e. the agent ending at the same location where
    it started, while visiting each of the other locations only once)
    '''
    #
    
    def __init__(self,parameters):
        #
        
        self.seed = None # for random number generator
        self.lx = 1
        self.ly = 1
        self.map_exists = False
        
        self.N_population = 200
        self.N_initial_duels = 4
        
        self.N_max_iter = 500000
        self.N_threshold = 10000

        self.verbose = True
        
        self.recombine = True
        
        self.distances = parameters['distances']
        
        self.N_nodes = len(self.distances)
        
        self.N_recombination_length = self.N_nodes//2
        
        self.rng = np.random.default_rng(seed=self.seed)


    def evaluate_fitness(self,states,perform_sum=True):
        #
        # self.distances[i,j] = distance from i to j
        #
        # np.shape(states) = (# of states, # of nodes)
        #
        # for every line in states, we want to create (N_nodes,2) matrix
        # with consecutive elements, take the corresponding elements in the
        # distances matrix, and sum over those
        states_extended = np.hstack((states,
                                     states[:,0].reshape(len(states),1)))
        #
        indices_0 = states_extended[:,:-1] # starting points for journeys
        indices_1 = states_extended[:,1:] # ending points for journeys
        traveled_distances = self.distances[indices_0,indices_1]
        if perform_sum:
            traveled_distances = traveled_distances.sum(axis=1)
        #
        # output shape = (# of states)
        return -traveled_distances


    def generate_random_states(self,N_states=1):
        states = np.ones([N_states,self.N_nodes],dtype=int)
        states *= np.arange(self.N_nodes)[np.newaxis,:]
        return self.rng.permuted(states,axis=1)


    def mutate_states(self,states,N_mutations=2):
        mutations = self.rng.choice(a=self.N_nodes,
                               size=(2*N_mutations,len(states)))
        #
        states_permuted = states.copy()
        for i,(indices_0,indices_1) in enumerate(zip(mutations[::2],
                                                     mutations[1::2])):
            values_0 = np.take_along_axis(arr=states_permuted,
                                        indices=indices_0[:,np.newaxis],
                                        axis=1).flatten()
            values_1 = np.take_along_axis(arr=states_permuted,
                                        indices=indices_1[:,np.newaxis],
                                        axis=1).flatten()
            #
            states_permuted[np.arange(len(states)),indices_1] = values_0
            states_permuted[np.arange(len(states)),indices_0] = values_1
        #
        return states_permuted
        

    def duel_states(self,states_0,states_1,fitness_0=None,fitness_1=None):
        if fitness_0 is None:
            fitness_0 = self.evaluate_fitness(states_0)
        if fitness_1 is None:
            fitness_1 = self.evaluate_fitness(states_1)
        #
        states_out = states_0.copy()
        fitness_out = fitness_0.copy()
        #
        mask = (fitness_0 < fitness_1) # mask[i] == True if and only if
                                # states_0[i] is longer than states_1[i]
        states_out[mask] = states_1[mask]
        fitness_out[mask] = fitness_1[mask]
        #
        return states_out, fitness_out
    

    def get_best_state_of_batch(self,states,fitness=None):
        #
        if fitness is None:
            fitness = self.evaluate_fitness(states)
        #
        return states[np.argmax(fitness)], fitness[np.argmax(fitness)]
        

    def recombine_states(self,states_0,states_1):
        #
        N_population = len(states_0)
        #
        indices = self.rng.choice(
                        a=self.N_nodes-self.N_recombination_length,
                        size=N_population
                                    )
        #
        #
        state_out = -np.ones([N_population,self.N_nodes],dtype=int)
        #
        for i,state_1 in enumerate(states_1):
            #
            state_out[i][indices[i]:indices[i]+self.N_recombination_length] \
              = states_0[i][indices[i]:indices[i]+self.N_recombination_length]
            #
            state_1 = state_1[~np.in1d(state_1,state_out[i])]
            mask = (state_out[i] < 0)
            state_out[i][mask] = state_1
        #
        #
        return state_out
    

    def run_genetic_algorithm(self,recombine=None):
        #
        if recombine is None:
            pass
        else:
            self.recombine = recombine
        #
        states_list = []
        for i in range(self.N_initial_duels):
            for j in range(self.N_initial_duels):
                states_list.append( 
                    self.generate_random_states(N_states=self.N_population) 
                                    )
        #
        for i in range(self.N_initial_duels):
            #
            states_out_list = []
            #
            for (states_0,states_1) in zip(states_list[::2],
                                           states_list[1::2]):
                states_out_list.append(self.duel_states(states_0=states_0,
                                                  states_1=states_1)[0])
            #
            states_list = states_out_list
        #
        states = states_list[0]
        fitness = self.evaluate_fitness(states=states)
        #
        shortest_path_length = [np.min(fitness)]
        #
        if self.recombine:
            N_mutate = self.N_population//2
            N_recombine = self.N_population - N_mutate
            self.N_recombine=N_recombine
        #
        for i in range(self.N_max_iter):
            #
            if self.recombine:
                #
                new_states = states.copy()
                #
                indices = self.rng.choice(a=self.N_population,
                                       size=N_mutate,
                                       replace=False)
                new_states[:N_mutate] = self.mutate_states(
                                                states=states[indices]
                                                            )
                #
                indices_0 = self.rng.choice(a=self.N_population,
                                       size=N_recombine,
                                       replace=False)
                indices_1 = self.rng.choice(a=self.N_population,
                                       size=N_recombine,
                                       replace=False)
                #
                new_states[N_mutate:] = self.recombine_states(
                                    states_0=states[indices_0],
                                    states_1=states[indices_1])
            else:
                new_states = self.mutate_states(states=states)
            #
            self.rng.shuffle(new_states,axis=0)
            #
            states, fitness = self.duel_states(states_0=states,
                                              states_1=new_states,
                                              fitness_0=fitness)
            #
            shortest_path_length.append(np.min(np.min(fitness)))
            #
            if i >= self.N_threshold:
                if len(np.unique(
                        np.array(shortest_path_length)[-self.N_threshold:]
                                )) == 1:
                    break
            #
        self.optimal_path = self.get_best_state_of_batch(states=states,
                                      fitness=fitness)
        return states, self.optimal_path
        


class traveling_salesman():
    '''
    This class takes a list of location names, uses the openroute_requests
    class to resolve them and obtain the distances between them, and then 
    uses the genetic_algorithm class to solve the traveling salesman problem
    for the given location names
    '''

    def __init__(self,parameters={}):
        #
        self.set_default_parameters()
        #
        self.set_parameters(parameters=parameters)
        #


    def set_default_parameters(self):
        #
        self.api_key_filename = None
        self.api_key = None
        #
        self.locations = []
        self.names = []
        #
        self.verbose = False
        #
        self.mode_of_transportation = 'driving-car'
        #
        self.N_runs = 3


    def set_parameters(self,parameters):
        #
        #
        try:
            self.api_key_filename = parameters['api_key_filename']
        except:
            pass
        #
        try: 
            self.api_key = parameters['api_key']
        except:
            pass
        #
        try: 
            self.verbose = parameters['verbose']
        except:
            pass
        #
        try:
            self.mode_of_transportation = parameters['mode_of_transportation']
        except:
            pass
        #
        try:
            self.N_runs = parameters['N_runs']
        except:
            pass

        self.initialize_openroute_requests()


    def initialize_openroute_requests(self):
        #
        self.set_openroute_api_key()
        #
        if not self.api_key:
            raise RuntimeError("No api key provided.")
        #
        #
        parameters_openroute = {'api_key':self.api_key,
                        'mode_of_transportation':self.mode_of_transportation
                                }
        #
        self.openroute_requests = openroute_requests(parameters_openroute)
        #


    def set_openroute_api_key(self,api_key=None):
        '''
        There are three possibilities:
        - set the api key as an argument of this function
        - set the api key via set_parameters({api_key:'your api key here'})
        - set the api key via a text file provided via 
                    set_parameters({api_key_filename:'filename.txt'})
        '''
        #
        if api_key:
            self.api_key = api_key
            return 0
        #
        if self.api_key:
            return 0
        #
        if self.api_key_filename:
            try:
                with open(self.api_key_filename,'r') as f:
                    f = f.read()
                    self.api_key = f.split('\n')[0]
                return 0
            except FileNotFoundError:
                    error_msg = ("Could not load openroute api key from file"
                                 " {0}".format(self.api_key_filename))
                    raise RuntimeError(error_msg)
        #
        error_msg = ("Could not load openroute api key")
        raise RuntimeError(error_msg)


    def set_locations(self,names=None):
        #
        self.locations = []
        self.names = []
        #
        for name in names:
            label, current_coordinates = self.openroute_requests.get_location(
                                                                    name=name)
            self.names.append(label)
            self.locations.append(current_coordinates)
        return self.names, self.locations


    def get_distance_matrix(self,locations=None):
        if not locations:
            locations = self.locations
        #
        self.distances = self.openroute_requests.get_distance_matrix(
                                            locations=locations)
        #
        return self.distances
    

    def solve(self,print_results=True):
        #
        distance_matrix = self.get_distance_matrix()
        #
        parameters = {'distances':distance_matrix}
        self.genetic_algorithm = genetic_algorithm(parameters=parameters)
        #
        shortest_length = np.inf
        #
        self.states_list = []
        self.shortest_path_list = []
        self.shortest_path_length_list = []
        #
        for i in range(self.N_runs):
            states,tmp = self.genetic_algorithm.run_genetic_algorithm(
                                                            recombine=True)
            current_indices, current_negative_shortest_length = tmp
            current_shortest_length = -current_negative_shortest_length
            #
            if current_shortest_length < shortest_length:
                shortest_length = current_shortest_length
                indices = current_indices
            #
            if self.verbose:
                status_msg = ('Minimization {0} of {1} completed. '
                              'Current shortest path length = {2:3.3f}')
                print(status_msg.format(i+1,N_runs,shortest_length))
        #
        indices = np.roll(indices,-np.argmax(indices == 0))
        #
        shortest_path_coordinates = np.array(self.locations)[indices]
        shortest_path_coordinates = np.vstack((shortest_path_coordinates,
                                shortest_path_coordinates[0][np.newaxis,:]))
        #
        trajectory_segments = \
            self.openroute_requests.get_trajectory_segments(
                                        locations=shortest_path_coordinates)
        #
        names = []
        for i,e in enumerate(indices):
            names.append(self.names[e])
        #
        trajectory_segment_lengths = \
            -self.genetic_algorithm.evaluate_fitness(
                            states=indices.reshape([1,len(indices)]),
                            perform_sum=False)[0]
        #
        self.shortest_path = {'length':shortest_length,
                   'indices':indices,
                   'coordinates':shortest_path_coordinates,
                   'names':names,
                   'trajectory_segments':trajectory_segments,
                   'trajectory_segment_lengths':trajectory_segment_lengths,
                   }
        #
        if print_results:
            print("Found shortest path:")
            #print("Location")
            for i,e in enumerate(trajectory_segment_lengths):
                print('{0}. {1}'.format(i+1,names[i%len(names)]))
                print('    {0} km'.format(e))
            print('{0}. {1}'.format(i+2,names[0]))
            print('\nTotal distance: {0:3.2f} km'.format(shortest_length))
        #
        return self.shortest_path
    

    def plot_shortest_path(self,filename=None,
                                width=1000,
                                height=700):
        #
        coordinates = self.shortest_path['coordinates']
        names = self.shortest_path['names']
        trajectory_segments = self.shortest_path['trajectory_segments']
        trajectory_segment_lengths = \
                            self.shortest_path['trajectory_segment_lengths']
        #
        fig = px.scatter_mapbox(lon=coordinates[:-1,0],
                            lat=coordinates[:-1,1],
                            #mapbox_style='open-street-map', 
                            mapbox_style='stamen-terrain',
                            #mapbox_style='stamen-watercolor',
                            width=width,
                            height=height,
                            zoom = 11,
                            hover_name = names,
                            )

        for i,e in enumerate(trajectory_segments):
            fig.add_traces(go.Scattermapbox(lon=e[:,0], lat=e[:,1],
                    mode='lines',
                    # 
                    name='{0:3.2f} km'.format(trajectory_segment_lengths[i]),
                    ))
        fig.show()

        if filename:
            pio.write_html(fig, file=filename, auto_open=False)

