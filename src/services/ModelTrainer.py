import time
import numpy as np
from secretflow.ml.linear.ss_sgd import SSRegression
from secretflow.data.split import train_test_split
from secretflow.device.driver import reveal
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report


class ModelTrainer:
    def __init__(self, spu, pyu_nodes):
        """
        Initializes the ModelTrainer with SPU and PYU nodes.
        :param spu: Secure Processing Unit for secure computation.
        :param pyu_nodes: List of PYU nodes.
        """
        self.spu = spu
        self.pyu_nodes = pyu_nodes
        self.model = SSRegression(spu)
        self.v_train_data = None
        self.v_test_data = None
        self.v_train_label = None
        self.v_test_label = None

    def split_data(self, v_data, label_data, split_factor=0.8, random_state=42):
        """
        Splits the data into training and testing sets.
        :param v_data: Vertically partitioned feature data.
        :param label_data: Vertically partitioned label data.
        :param split_factor: Proportion of data to use for training.
        :param random_state: Random seed for reproducibility.
        :return: None.
        """
        self.v_train_data, self.v_test_data = train_test_split(v_data, train_size=split_factor, random_state=random_state)
        self.v_train_label, self.v_test_label = train_test_split(label_data, train_size=split_factor, random_state=random_state)

    def train_model(self, epochs=5, learning_rate=0.3, batch_size=32, sig_type='t1', reg_type='logistic', penalty='l2', l2_norm=0.1):
        """
        Trains the model using secure computation.
        :param epochs: Number of epochs to train.
        :param learning_rate: Learning rate for the model.
        :param batch_size: Batch size for training.
        :param sig_type: Sigmoid type.
        :param reg_type: Regression type (logistic regression).
        :param penalty: Regularization penalty type.
        :param l2_norm: L2 normalization factor.
        :return: The training time.
        """
        start = time.time()
        self.model.fit(
            self.v_train_data,  # X
            self.v_train_label,  # Y
            epochs,
            learning_rate,
            batch_size,
            sig_type,
            reg_type,
            penalty,
            l2_norm
        )
        train_time = time.time() - start
        return train_time

    def make_predictions(self):
        """
        Makes predictions on the test set.
        :return: Tuple of predicted labels and prediction time.
        """
        start = time.time()
        spu_yhat = self.model.predict(self.v_test_data)
        yhat = reveal(spu_yhat)
        predict_time = time.time() - start
        return yhat, predict_time

    def evaluate_model(self, yhat):
        """
        Evaluates the model using AUC, accuracy, and classification report.
        :param yhat: The predicted labels.
        :return: A dictionary of evaluation metrics.
        """
        y = reveal(self.v_test_label.partitions[self.pyu_nodes[0]])

        auc_score = roc_auc_score(y, yhat)

        binary_class_results = np.where(yhat > 0.5, 1, 0)

        acc_score = accuracy_score(y, binary_class_results)

        class_report = classification_report(y, binary_class_results)

        return {
            'auc_score': auc_score,
            'accuracy_score': acc_score,
            'classification_report': class_report
        }

    def run(self, v_data, label_data):
        """
        The main method to run the entire training, prediction, and evaluation pipeline.
        :param v_data: Vertically partitioned feature data.
        :param label_data: Vertically partitioned label data.
        :return: Dictionary with training time, prediction time, and evaluation metrics.
        """
        self.split_data(v_data, label_data)

        train_time = self.train_model()

        yhat, predict_time = self.make_predictions()

        evaluation_metrics = self.evaluate_model(yhat)

        return {
            'train_time': train_time,
            'predict_time': predict_time,
            **evaluation_metrics
        }