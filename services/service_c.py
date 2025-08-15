from service_template import MicroserviceTemplate
import threading

if __name__ == "__main__":
    service = MicroserviceTemplate("service_c", 8003, ["service_d"])
    service.run_background_tasks()
    service.start()
