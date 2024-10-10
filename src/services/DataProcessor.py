from secretflow.data import FedNdarray, PartitionWay
from secretflow.device.driver import wait
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_breast_cancer


class DataProcessor:
    def __init__(self, pyu_nodes):
        """
        Initialize with the list of PYU nodes.
        pyu_nodes: List of PYU instances representing different parties.
        """
        self.pyu_nodes = pyu_nodes
        self.total_columns = 30  # This is specific to the breast cancer dataset

    def read_x(self, start, end):
        """
        Function to read and scale features between start and end indices.
        This is meant to be run on each node.
        """
        data = load_breast_cancer()['data']
        scaler = StandardScaler()
        data = scaler.fit_transform(data)
        return data[:, start:end]

    def read_y(self):
        """
        Function to read the target labels (Y values).
        This is meant to be run on the node holding the label data.
        """
        return load_breast_cancer()['target']

    def partition_data(self):
        """
        Dynamically partitions the dataset across the available nodes.
        Each node gets an equal or nearly equal number of columns.
        Returns the partitioned data as a FedNdarray.
        """

        # Create partitions for each node
        partitions = self._make_partitions()

        # Create FedNdarray for vertically partitioned data
        v_data = FedNdarray(
            partitions=partitions,
            partition_way=PartitionWay.VERTICAL,
        )

        # Assign labels to the first node
        label_data = FedNdarray(
            partitions={self.pyu_nodes[0]: self.pyu_nodes[0](self.read_y)()},
            partition_way=PartitionWay.VERTICAL,
        )

        # Wait for data loading to finish
        wait([p.data for p in v_data.partitions.values()])
        wait([p.data for p in label_data.partitions.values()])

        return v_data, label_data

    def _make_partitions(self) -> dict:
        """
        Partition the data and return the partitioned data.
        """
        num_nodes = len(self.pyu_nodes)
        columns_per_node = self.total_columns // num_nodes
        remainder = self.total_columns % num_nodes

        partitions = {}
        start_col = 0

        for i, node in enumerate(self.pyu_nodes):
            # Calculate end column, distribute remainder to the first few nodes if necessary
            end_col = start_col + columns_per_node
            if i < remainder:
                end_col += 1

            # Assign partition for this node's columns
            partitions[node] = node(self.read_x)(start_col, end_col)
            start_col = end_col  # Move the start column for the next node
        
        return partitions