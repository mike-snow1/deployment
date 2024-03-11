import logging
import matplotlib.pyplot as plt

from py3dbp import Packer, Bin, Item
from mpl_toolkits.mplot3d import Axes3D


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimalPackingFinder(object):
    def __init__(self, reduction_factor=0.95):
        self.items = None
        self.reduction_factor = reduction_factor
        self.optimal_dimensions = None
        self.last_successful_packer = None
    
    
    def initial_estimate_dimensions(self):
        """
        Calculate dimensions for a box to fit all given items.

        Parameters:
        items (dict): A dictionary of items with their dimensions and weights.

        Returns:
        tuple: Suggested dimensions for the box (width, height, depth).
        """
        # Initialize sums and maximums
        sum_width = sum(item['width'] for item in self.items.values())
        sum_height = sum(item['height'] for item in self.items.values())
        sum_depth = sum(item['depth'] for item in self.items.values())
        max_width = max(item['width'] for item in self.items.values())
        max_height = max(item['height'] for item in self.items.values())
        max_depth = max(item['depth'] for item in self.items.values())

        # Box dimensions based on the sum of dimensions and maximums
        box_width = max(sum_width, max_width)
        box_height = max(sum_height, max_height)
        box_depth = max(sum_depth, max_depth)

        return box_width, box_height, box_depth

        
#     def initial_estimate_dimensions(self):
#         total_volume = sum(item['width'] * item['height'] * item['depth'] for item in self.items.values())
#         max_width = max(item['width'] for item in self.items.values())
#         max_height = max(item['height'] for item in self.items.values())
#         max_depth = max(item['depth'] for item in self.items.values())
        
#         volume_side = (total_volume ** (1/3))
#         return max(max_width, volume_side), max(max_height, volume_side), max(max_depth, volume_side)

    
    def check_all_items_packed(self, bin_dimensions, return_packer=False):
        packer = Packer()
        bin = Bin("Bin", *bin_dimensions, 1000000)  # Large weight capacity
        packer.add_bin(bin)
        
        for name, dims in self.items.items():
            packer.add_item(Item(name, dims['width'], dims['height'], dims['depth'], 0))  # Weight is set to 0
        
        packer.pack()
        
        if return_packer:
            return sum(len(b.items) for b in packer.bins) == len(self.items), packer
        else:
            return sum(len(b.items) for b in packer.bins) == len(self.items)

        
    def find_optimal_bin_dimensions(self):
        bin_dimensions = self.initial_estimate_dimensions()
        print(f"Initial estimate: {bin_dimensions}")
        optimal_found = False
        
        while not optimal_found:
            all_fit, packer = self.check_all_items_packed(bin_dimensions, return_packer=True)
            if all_fit:
                # If all items are packed, reduce the bin size
                bin_dimensions = tuple(dim * self.reduction_factor for dim in bin_dimensions)
                print(f"Reducing dimensions to: {bin_dimensions}")
                self.last_successful_packer = packer
            else:
                # If not all items fit, use the last successful dimensions for the optimal size
                bin_dimensions = tuple(dim / self.reduction_factor for dim in bin_dimensions)
                print(f"Found optimal dimensions (previous iteration): {bin_dimensions}")
                optimal_found = True
        
        self.optimal_dimensions = bin_dimensions

        
    def visualize_packing(self):
        if not self.last_successful_packer:
            print("No packing to visualize. Please run find_optimal_bin_dimensions first.")
            return
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        for bin in self.last_successful_packer.bins:
            for item in bin.items:
                x, y, z = item.position
                dx, dy, dz = item.get_dimension()
                ax.bar3d(x, y, z, dx, dy, dz, alpha=0.5)
          
        bin_width, bin_height, bin_depth = self.optimal_dimensions
                
        bin_edges = [
            [[0, 0, 0], [bin_width, 0, 0], [bin_width, bin_height, 0], [0, bin_height, 0], [0, 0, 0]],
            [[0, 0, bin_depth], [bin_width, 0, bin_depth], [bin_width, bin_height, bin_depth], [0, bin_height, bin_depth], [0, 0, bin_depth]],
            [[0, 0, 0], [0, 0, bin_depth]],
            [[bin_width, 0, 0], [bin_width, 0, bin_depth]],
            [[bin_width, bin_height, 0], [bin_width, bin_height, bin_depth]],
            [[0, bin_height, 0], [0, bin_height, bin_depth]]
        ]
        ax.set_xlabel('Width')
        ax.set_ylabel('Height')
        ax.set_zlabel('Depth')     
        
        plt.show()

    def predict(self, X, features_names=None):  # change from get-predictions to predict
        """
        :Output: JSON output from API
        :param review_information: dictionary/json of review information
        """
    #     information = json.load(review_information)
        
        
        if(len(X) > 0):            
            logger.info(f'Input data: {X}')
            logger.info(f'Input data type: {type(X)}')
        
        self.items = X
        self.find_optimal_bin_dimensions()
        
        width, height, depth = self.optimal_dimensions

        return {'width': width,
                'height': height,
                'depth': depth}
    