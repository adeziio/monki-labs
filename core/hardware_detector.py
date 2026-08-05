import platform


class HardwareDetector:


    def detect(self):

        hardware = {

            "os":
            platform.system(),

            "device":
            "cpu",

            "gpu_available":
            False

        }


        try:

            import torch


            if torch.cuda.is_available():

                hardware["device"] = "cuda"

                hardware["gpu_available"] = True


            elif (
                hasattr(torch.backends, "mps")
                and
                torch.backends.mps.is_available()
            ):

                hardware["device"] = "mps"

                hardware["gpu_available"] = True


        except Exception:

            pass


        return hardware