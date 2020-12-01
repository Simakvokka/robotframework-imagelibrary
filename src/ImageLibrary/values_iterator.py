from ImageLibrary import utils

class ValuesIterator:
    def __init__(self, values, length):
        self.iter = values
        self.length = length

    def __len__(self):
        return self.length

    def __iter__(self):
        return self

    def __next__(self):
        return self.iter.__next__()


class Value:
    def __init__(self, name, config):
        self.name = name
        if isinstance(config, list):
            #simple list of values
            self.values = config
        elif isinstance(config, dict):
            assert "begin" in config and "end" in config, "begin and end values must be defined for {}".format(name)
            begin = int(config["begin"])
            end = int(config["end"])
            step = int(config["step"]) if "step" in config else 1
            #we want to include last value, so increase end
            self.values = list(range(begin, end+step, step))
        else:
            #only one element
            self.values = [config]

    @utils.add_error_info
    def iterate_all_values(self, reverse=False):
        reverse = utils.to_bool(reverse)
        print(*iter(self.values))
        return ValuesIterator(iter(self.values) if not reverse else reversed(self.values), len(self.values))


    @utils.add_error_info
    def get_value_from_config(self, index):
        index = int(index)
        return self.values[index-1]


    @utils.add_error_info
    def get_last_value_from_config(self):
        return self.values[-1]


    @utils.add_error_info
    def get_values_from_config(self):
        return self.values
