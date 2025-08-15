from service_template import MicroserviceTemplate
import threading

if __name__ == "__main__":
    service = MicroserviceTemplate("service_a", 8001, ["service_b"])
    service.run_background_tasks()
    service.start()
