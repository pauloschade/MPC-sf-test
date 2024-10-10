from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.services.RayNode import RayNode
from src.services.CommandExecutor import CommandExecutor
from src.types.SingletonMeta import SingletonMeta


class NodeRequest(BaseModel):
  ip: str = '127.0.0.1'
  port: int = 6379
  node_type: str = 'head'  # 'head' or 'worker'
  name: str
  resources: int = 16

class PartiesService(metaclass=SingletonMeta):
  def __init__(self):
    self.parties = []
    self.head = None
    self.executor = CommandExecutor()


  def add_node(self, node_info: NodeRequest):
    """
    Add a new RayNode to the Parties instance.
    If the node type is 'head', it will be set as the head.
    Otherwise, it will be added as a regular node.
    """
    node = RayNode(
        ip=node_info.ip,
        port=node_info.port,
        node_type=node_info.node_type,
        name=node_info.name,
        resources=node_info.resources
    )

    if node_info.node_type == 'head':
        self.set_head(node)
    else:
        self.add_party(node)

    return f"Node {node_info.name} added successfully."

  def add_party(self, party: RayNode):
    self.parties.append(party)
  
  def set_head(self, head: RayNode):
    self.head = head

  def create(self):
    if not self.head:
      raise ValueError("Head node must be set before creating parties.")

    command = self.head.create()
    self.executor.run_command(command)

    for party in self.parties:
      command = party.create()
      self.executor.run_command(command)
      
    return "Parties created successfully"


# Parties API Router
PartiesRouter = APIRouter(
    prefix="/parties", tags=["parties"]
)


@PartiesRouter.post(
    "/add_node/",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
    summary="Adds a node to the cluster",
    description="Adds a RayNode to the cluster. Can be a head or worker node."
)
async def add_node(
    node_info: NodeRequest,
):
    try:
        parties_service = PartiesService()
        result = parties_service.add_node(node_info)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@PartiesRouter.post(
    "/create_cluster/",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
    summary="Creates the cluster",
    description="Creates the cluster using the defined head and worker nodes."
)
async def create_cluster():
    try:
        parties_service = PartiesService()
        result = parties_service.create()

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))