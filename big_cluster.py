import os
from unionfind_bigcluster import UFNode, UnionFind
import itertools
import time

EDGE_COST = 1

class BigCluster:
    def __init__(self, filename: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clustering_big.txt'), min_spacing: int = 3):  # by default, looks for the input in file "clustering_big.txt" in the same directory as this script
        self.edge_costs = []
        self.edge_endpoints = {}  # { edge_cost: {(endpoint, endpoint)} } - still allows for (and there will be) duplicate edges with endpoints reversed - doesn't matter because the 2 endpoints will be unioned the first time their edge is considered, meaning the 2nd will be overlooked
        self.min_spacing = min_spacing
        self.cluster_field = UnionFind()
        self.load_node_data(filename)

    def load_node_data(self, filename: str):
        with open(filename) as fh:
            metadata = fh.readline().split()
            print('Loading ' + metadata[0] + ' ' + metadata[1] + '-bit nodes')
            raw_node_str = fh.readline()
            while raw_node_str:
                self.cluster_field.add_node_str(raw_node_str.strip().replace(' ', ''))
                raw_node_str = fh.readline()
            print(f'Loaded {len(self.cluster_field.nodes)} nodes')

    def add_relevant_edges(self):
        for node_str in self.cluster_field.nodes:
            possible_neighbors = self._calculate_possible_neighbors_iter(node_str)
            present_neighbors = self._find_present_neighbors(possible_neighbors)

            # add edges
            for edge_cost_neighbors in present_neighbors:
                if EDGE_COST not in self.edge_endpoints:
                    self.edge_endpoints[EDGE_COST] = set()
                for neighbor_str in edge_cost_neighbors:
                    self.edge_endpoints[EDGE_COST].add((node_str, neighbor_str))

    def _calculate_possible_neighbors_iter(self, node_str: str) -> list:
        possible_edge_costs = range(self.min_spacing)
        possible_neighbors = [set() for cost in possible_edge_costs] # [{possible neighbors of cost 1}, {of cost 2}, ...]
        positions = [i for i in range(len(node_str))]
        neighbor_cost_index = 0
        for edge_cost in possible_edge_costs:
                    swap_indices = itertools.combinations(positions, edge_cost)
                    for swap_index_tup in swap_indices:
                        node_str_swapping = list(node_str)
                        for index in swap_index_tup:
                            node_str_swapping[index] = _swap_digit(node_str_swapping[index])
                        possible_neighbors[neighbor_cost_index].add(''.join(node_str_swapping))
                    neighbor_cost_index += 1
        return possible_neighbors

    def _find_present_neighbors(self, possible_neighbors: list) -> list:
        present_neighbors = [set() for edge_cost_possible_neighbors in possible_neighbors]
        present_neighbors_index = 0
        for edge_cost_possible_neighbors in possible_neighbors:
            for possible_neighbor_str in edge_cost_possible_neighbors:
                if possible_neighbor_str in self.cluster_field.nodes:
                    present_neighbors[present_neighbors_index].add(possible_neighbor_str)
            present_neighbors_index += 1
        return present_neighbors

    def get_k_min_spacing(self):
        edge_generator = self._yield_edges()
        cost_and_endpoints = next(edge_generator)
        while cost_and_endpoints:
            cost, u, v = cost_and_endpoints[0], cost_and_endpoints[1][0], cost_and_endpoints[1][1]
            if self.cluster_field.find(u) != self.cluster_field.find(v):
                    self.cluster_field.union(u,v)
            try:
                cost_and_endpoints = next(edge_generator)
            except StopIteration:  # upon exhausting all edges under the minimum spacing
                return len(self.cluster_field.component_sizes)

    def _yield_edges(self):
        for edge_cost in self.edge_endpoints:  # this depends on self.edge_endpoints being sorted
            edges = self.edge_endpoints[edge_cost]
            while edges:
                yield edge_cost, edges.pop()

def _swap_digit(binary_digit: str):
    if binary_digit == '1':
        return '0'
    elif binary_digit == '0':
        return '1'
    else:
        raise ValueError('non-binary string value found')

if __name__ == '__main__':
    
        load_start = time.time()
        cluster_test = BigCluster(min_spacing=3)
        load_finish = time.time()
        print(f'Initialized clustering object in {load_finish-load_start}s')

        add_edges_start = time.time()
        cluster_test.add_relevant_edges()
        add_edges_end = time.time()
        print(f'Added relevant edges in {add_edges_end - add_edges_start}s')

        get_k_start = time.time()
        result = cluster_test.get_k_min_spacing()
        get_k_finish = time.time()
        print(f'Calculated k={result} clusters in {get_k_finish-get_k_start}s \n')
        