class RayNode:
    def __init__(self, ip: str, port: int, node_type: str, name: str, resources: int = 16):
      self.ip = ip
      self.port = port
      self.type = node_type
      self.name = name
      self.resources = resources

    def create(self) -> str:
      if self.type == 'head':
          return self._create_head()
      else:
          return self._create()

    def _create(self) -> str:
      resources_str = self._make_resources_str()

      command = f'ray start --address="{self.ip}:{self.port}" --resources={resources_str} --disable-usage-stats'

      return command

    def _create_head(self) -> str:
      resources_str = self._make_resources_str()

      command = f'ray start --head --node-ip-address="{self.ip}" --port="{self.port}" --resources={resources_str} --include-dashboard=False --disable-usage-stats'
      return command

    def _make_resources_str(self) -> str:
      resources = {self.name: self.resources}

      return str(resources).replace("'", '"')