from .Parties import PartiesService, NodeRequest
from .MPC import MPCService
from fastapi import APIRouter, status

MockRouter = APIRouter(
    prefix="/mock", tags=["mock"]
)

@MockRouter.post(
    "/gen/",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
    summary="Mock endpoint",
    description="Mock endpoint for testing purposes."
)
async def gen():
    try:
        node_head = NodeRequest(name='p')
        node_worker = NodeRequest(name='w', node_type='worker')

        parties_service = PartiesService()
        parties_service.add_node(node_head)
        parties_service.add_node(node_worker)
        parties_service.create()

        mpc_service = MPCService()
        mpc_service.initialize()

        return "Mock endpoint"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

