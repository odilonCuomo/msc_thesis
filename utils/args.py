class Args:
  def __init__(self):
      self.num_runs = 25

def get_path_name(path, args):
   for attr_name, attr_val in list(args.__dict__.items()):
        path += attr_name + str(attr_val) + "_"
   l = len(path)
   if path[l - 1] == "_":
       path = path[: l - 1]
   return path