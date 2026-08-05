class DeviceManager:


    def __init__(self, hardware):

        self.device = (
            hardware["device"]
        )



    def get_device(self):

        return self.device



    def is_gpu(self):

        return self.device in [

            "cuda",

            "mps"

        ]