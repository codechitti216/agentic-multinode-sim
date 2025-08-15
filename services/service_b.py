from service_template import MicroserviceTemplate
import threading

if __name__ == "__main__":
    service = MicroserviceTemplate("service_b", 8002, ["service_c"])
    service.run_background_tasks()
    service.start()
