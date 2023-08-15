class Args:
  def __init__(self):
    pass

def get_path_name(args):
    path = ""
    for attr_name, attr_val in list(args.__dict__.items()):
        path += attr_name + str(attr_val) + "_"
    path = path[: - 1]
    return path