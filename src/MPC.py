from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
import secretflow as sf
import numpy as np

from .Parties import PartiesService
from .services.DataProcessor import DataProcessor
from .services.ModelTrainer import ModelTrainer
from src.types.SingletonMeta import SingletonMeta

class MPCService(metaclass=SingletonMeta):
    def __init__(self):
        self.parties = PartiesService()
        self.pyu_nodes = []
        self.spu = None

    def initialize(self):
        """
        Initialize SecretFlow and the parties, ensuring nodes are ready for computation.
        """
        # Initialize SecretFlow in Standalone Mode with all parties
        sf.init([party.name for party in self.parties.parties + [self.parties.head]], address='local')

        # Dynamically assign PYU instances from the parties
        self.pyu_nodes = [sf.PYU(party.name) for party in self.parties.parties + [self.parties.head]]

        # Initialize SPU for secure processing
        self.spu = sf.SPU(sf.utils.testing.cluster_def([party.name for party in self.parties.parties + [self.parties.head]]))

        return f"initialized, {len(self.pyu_nodes)}, nodes"

    def run(self):
        """
        Run the multi-party computation and secure training, return time and classification report.
        """
        # Initialize data processor
        data_processor = DataProcessor(self.pyu_nodes)
        # Read and partition data

        v_data, label_data = data_processor.partition_data()
        # Initialize model trainer

        model_trainer = ModelTrainer(self.spu, self.pyu_nodes)

        # Run model trainer
        results = model_trainer.run(v_data, label_data)

        return results


MPCRouter = APIRouter()


@MPCRouter.post(
    "/initialize/",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
    summary="Initializes the MPC environment",
    description="Initializes the multi-party computation environment using SecretFlow."
)
async def initialize_mpc():
    """
    Endpoint to initialize the MPC system.
    """
    try:
        mpc_service = MPCService()
        ret = mpc_service.initialize()
        return ret
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to initialize MPC: {str(e)}")


@MPCRouter.post(
    "/run/",
    # response_model=Dict[str, str],
    # response_model=str,
    status_code=status.HTTP_200_OK,
    summary="Runs the MPC task",
    description="Runs the multi-party computation task and returns metrics like training time, accuracy, and AUC score."
)
async def run_mpc():
    """
    Endpoint to run the MPC task.
    """
    try:
        mpc_service = MPCService()
        result = mpc_service.run()
        # result_str = f"Train Time: {result['train_time']} seconds\nPredict Time: {result['predict_time']} seconds\nAUC Score: {result['auc_score']}\nAccuracy Score: {result['accuracy_score']}\nClassification Report:\n{result['classification_report']}"

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run MPC: {str(e)}")