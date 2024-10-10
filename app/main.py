from fastapi import FastAPI
import secretflow as sf
import spu
from src.MPC import MPCRouter
from src.Parties import PartiesRouter
from src.Mock import MockRouter

# from infrastructure.routers.ProductRouter import ProductRouter
# from infrastructure.routers.StockRouter import StockRouter
# from infrastructure.routers.TransactionRouter import TransactionRouter

app = FastAPI()

# print('The version of SecretFlow: {}'.format(sf.__version__))
# # In case you have a running secretflow runtime already.
# sf.shutdown()
# sf.init(['alice', 'bob', 'carol', 'dave'], address='local')
# aby3_config = sf.utils.testing.cluster_def(parties=['alice', 'bob', 'carol'])
# spu_device = sf.SPU(aby3_config)

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(MPCRouter)
app.include_router(PartiesRouter)
app.include_router(MockRouter)

# # Test endpoint to check if SecretFlow is working in simulation mode
# @app.get("/secretflow-test")
# def secretflow_test():
#     def get_carol_assets():
#         return 1000000


#     def get_dave_assets():
#         return 1000002


#     carol, dave = sf.PYU('carol'), sf.PYU('dave')

#     carol_assets = carol(get_carol_assets)()
#     dave_assets = dave(get_dave_assets)()
#     def get_winner(carol, dave):
#         return carol > dave

#     winner = spu_device(get_winner)(carol_assets, dave_assets)

#     win = sf.reveal(winner)

#     str_carol_assets = str(carol_assets)
#     str_dave_assets = str(dave_assets)

#     win_str = 'Carol' if win else 'Dave'

#     return {"Winner": win_str, "Carol Assets": str_carol_assets, "Dave Assets": str_dave_assets}
#     # return {"Hello": "World"}




# # def main() -> None:
# #     """Invoke the entrypoint function of the script."""
# #     uvicorn.run("main:app", host="0.0.0.0", reload=True)


# # if __name__ == "__main__":
# #     main()